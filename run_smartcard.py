import os

from fastapi import FastAPI, Request, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

import requests
import uvicorn

from dotenv import load_dotenv
load_dotenv()

import sqlite3

from modules.database import init_db, get_db

init_db()


app = FastAPI(debug=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

security = HTTPBasic()
session_secret_key = os.getenv("SESSION_SECRET_KEY", "supersecretkey")
app.add_middleware(SessionMiddleware, secret_key=session_secret_key)

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    conn, c = get_db()

    if request.session.get("user_id"):
        user = c.execute("SELECT * FROM users WHERE userid = ?", (request.session.get("user_id"),)).fetchone()
    else:
        user = None

    allbusinesses = []

    for x in c.execute("SELECT business_name, username FROM users").fetchall():
        allbusinesses.append((x["business_name"], x["username"]))

    allbusinesses = tuple(allbusinesses)

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": user, "allbusinesses": allbusinesses}
    )

# We use INSERT OR IGNORE because 'service_name' is UNIQUE

# users:
# userid, name, email (unique), password, contact, business_name, business_bio, business_website, business_logo_url, business_email, optional_address, username (unique), 
# created_at, updated_at, whatsapp_number, optional_insta, optional_facebook, optional_youtube, 

# images:
# imageid, userid, image_url, created_at, updated_at

# services:
# serviceid, userids (seperated by commas, default none), service_name

# admin:
# adminid, name, email, password


# we will store admin in sesison
def admin_required(request: Request):
    if not request.session.get("admin_username"):
        return False
    else:
        username = request.session.get("admin_username")
        admin_username = os.getenv("ADMIN_USERNAME")
        if username == admin_username:
            return True
        return False


# add user only if admin
@app.get("/adduser", response_class=HTMLResponse)
async def add_user_form(request: Request, is_admin: bool = Depends(admin_required)):
    if not is_admin:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"request": request}
        )
    return templates.TemplateResponse(
        request=request,
        name="adduser.html"
    )

@app.get("/delete_user", response_class=HTMLResponse)
async def delete_user_form(request: Request, is_admin: bool = Depends(admin_required)):
    if not is_admin:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"request": request}
        )
    return templates.TemplateResponse(
        request=request,
        name="deleteuser.html"
    )

@app.post("/delete_user")
async def delete_user(request: Request):
    if not admin_required(request):
        raise HTTPException(status_code=403, detail="Admin access required.")
    form = await request.json()
    username = form.get("username")
        
    conn, c = get_db()
    c.execute("SELECT * FROM users WHERE username = ? or email = ?", (username, username))
    user = c.fetchone()
    if user is None:
        conn.close()
        return {"message": f"User '{username}' does not exist."}
    else:
        c.execute("DELETE FROM images WHERE userid = ?", (user["userid"],))
        c.execute("DELETE FROM users WHERE username = ? or email = ?", (username, username))
        conn.commit()
        conn.close()
    return {"message": f"User '{username}' deleted successfully."}


@app.post("/add_user")
async def add_user(request: Request):
    if not admin_required(request):
        raise HTTPException(status_code=403, detail="Admin access required.")
    form = await request.json()
    name = form.get("name")
    email = form.get("email")
    password = form.get("password")
    username = form.get("username")
    print(f"Received data: name={name}, email={email}, password={password}, username={username}")
    conn, c = get_db()
    c.execute("""
        INSERT OR IGNORE INTO users (name, email, password, username)
        VALUES (?, ?, ?, ?)
    """, (name, email, password, username))
    conn.commit()
    conn.close()
    return {"message": "User added successfully."}


@app.get("/business/{username}", response_class=HTMLResponse)
async def business_card(request: Request, username: str):
    conn, c = get_db()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user is None:
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"request": request}
        )
    return templates.TemplateResponse(
        request=request,
        name="business_view.html",
        context={"request": request, "user": user}
    )


@app.post("/edit_business_details/{username}", response_class=JSONResponse)
async def edit_business_details(request: Request, username: str):
    conn, c = get_db()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user is None:
        conn.close()
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"request": request}
        )
    
    form = await request.json()
    name = form.get("name")
    password = form.get("password")
    contact = form.get("contact")
    business_name = form.get("business_name")
    business_bio = form.get("business_bio")
    business_website = form.get("business_website")
    business_email = form.get("business_email")
    optional_address = form.get("optional_address")
    whatsapp_number = form.get("whatsapp_number")
    optional_insta = form.get("optional_insta")
    optional_facebook = form.get("optional_facebook")
    optional_youtube = form.get("optional_youtube")

    c.execute("""
            UPDATE users
            SET name=?, password=?, contact=?, business_name=?, business_bio=?, business_website=?, business_email=?, 
             optional_address=?, whatsapp_number=?, optional_insta=?, optional_facebook=?, optional_youtube=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE username=?
        """, (name, password, contact, business_name, business_bio, business_website, business_email,
            optional_address, whatsapp_number, optional_insta, optional_facebook, optional_youtube, username))
    conn.commit()
    conn.close()

    return JSONResponse({"message": "Business details updated successfully."})


@app.post("/edit_business_details/{username}/upload_edit_logo", response_class=JSONResponse)
async def upload_edit_logo(request: Request, username: str):
    conn, c = get_db()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    if user is None:
        conn.close()
        return templates.TemplateResponse(
            request=request,
            name="404.html",
            context={"request": request}
        )
    
    form = await request.form()
    file = form.get("file")
    if not file:
        return JSONResponse({"message": "No file uploaded."}, status_code=400)

    # Save the uploaded file to the static directory
    file_location = f"static/uploads/{user['userid']}_{username}_logo.png"
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Update the user's business_logo_url in the database
    db_path = f"/{file_location}"

    c.execute("UPDATE users SET business_logo_url=?, updated_at=CURRENT_TIMESTAMP WHERE username=? ", (db_path, username))
    conn.commit()
    conn.close()

    return JSONResponse({"message": "Business logo updated successfully.", "logo_url": file_location})


@app.get("/edit_business_details/{username}", response_class=HTMLResponse)
async def edit_business_details_form(request: Request, username: str):
    conn, c = get_db()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return templates.TemplateResponse(
        request=request,
        name="edit_business.html",
        context={"request": request, "user": user}
    )


@app.api_route("/login", methods=["GET", "POST"])
async def login(request: Request):
    if request.method == "POST":
        form = await request.json()
        username = form.get("username")
        password = form.get("password")
        email = form.get("email")

        conn, c = get_db()
        c.execute("SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?", (username, email, password))
        user = c.fetchone()

        if user:
            # set session for the user
            request.session["user_id"] = user["userid"]
            return {"message": "Login successful.", "user": user["username"]}
        else:
            return {"message": "Invalid credentials."}

        conn.close()

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request}
    )


@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context={"request": request}
    )

@app.post("/admin/login")
async def admin_login_post(request: Request):
   # same as /login just set username in session
    form = await request.json()
    username = form.get("username")
    password = form.get("password")

    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_email = os.getenv("ADMIN_EMAIL")

    if ((username == admin_username or username == admin_email) and password == admin_password):
        request.session["admin_username"] = admin_username
        return {"message": "Admin login successful."}
    else:
        return {"message": "Invalid admin credentials."}


@app.post("/admin/logout")
async def admin_logout(request: Request):
    request.session.pop("admin_username", None)
    return {"message": "Admin logged out successfully."}

@app.post("/logout")
async def logout(request: Request):
    request.session.pop("user_id", None)
    return {"message": "User logged out successfully."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8520)