import sqlite3

# users:
# userid, name, email (unique), password, contact, business_name, business_bio, business_website, business_logo_url, optional_address, username (unique), created_at, updated_at, whatsapp_number, optional_insta, optional_facebook, optional_youtube,

# images:
# imageid, userid, image_url, created_at, updated_at

# services:
# serviceid, userids (seperated by commas, default none), service_name

# admin:
# adminid, name, email, password

def get_db():
    conn = sqlite3.connect("business_card.db")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    return conn, c
    

def init_db():
    conn, c = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            userid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            contact TEXT,
            business_name TEXT,
            business_bio TEXT,
            business_website TEXT,
            business_logo_url TEXT,
            optional_address TEXT,
            username TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            whatsapp_number TEXT,
            optional_insta TEXT,
            optional_facebook TEXT,
            optional_youtube TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS images (
            imageid INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            image_url TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userid) REFERENCES users(userid)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS services (
            serviceid INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_services (
            userid INTEGER NOT NULL,
            serviceid INTEGER NOT NULL,
            PRIMARY KEY (userid, serviceid),
            FOREIGN KEY (userid) REFERENCES users(userid),
            FOREIGN KEY (serviceid) REFERENCES services(serviceid)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            adminid INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()