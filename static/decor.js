(function () {
	const presets = [
		{ x: 6, y: 16, angle: 88, length: 48, opacity: 0.72 },
		{ x: 92, y: 22, angle: -86, length: 44, opacity: 0.68 },
		{ x: 12, y: 76, angle: 18, length: 34, opacity: 0.62 },
		{ x: 88, y: 66, angle: -28, length: 40, opacity: 0.58 },
		{ x: 22, y: 30, angle: 62, length: 36, opacity: 0.55 },
		{ x: 78, y: 82, angle: -54, length: 38, opacity: 0.56 },
		{ x: 50, y: 10, angle: 4, length: 30, opacity: 0.46 },
		{ x: 48, y: 92, angle: 0, length: 28, opacity: 0.42 },
		{ x: 4, y: 48, angle: 74, length: 52, opacity: 0.6 },
		{ x: 96, y: 54, angle: -72, length: 46, opacity: 0.57 },
		{ x: 28, y: 8, angle: 32, length: 24, opacity: 0.5 },
		{ x: 72, y: 94, angle: -34, length: 26, opacity: 0.49 },
		{ x: 18, y: 60, angle: 14, length: 42, opacity: 0.53 },
		{ x: 82, y: 40, angle: -12, length: 44, opacity: 0.52 },
		{ x: 40, y: 88, angle: 82, length: 32, opacity: 0.47 },
		{ x: 60, y: 18, angle: -80, length: 34, opacity: 0.44 },
	];

	const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
	const randomBetween = (min, max) => Math.random() * (max - min) + min;

	const buildField = () => {
		if (document.body.dataset.lightningDecorated === "true") {
			return;
		}

		document.body.dataset.lightningDecorated = "true";

		const field = document.createElement("div");
		field.className = "lightning-field";

		const streakCount = window.innerWidth < 640 ? 8 : 14;
		for (let index = 0; index < streakCount; index += 1) {
			const preset = presets[index % presets.length];
			const line = document.createElement("span");
			line.className = "lightning-line";

			const x = clamp(preset.x + randomBetween(-8, 8), 2, 98);
			const y = clamp(preset.y + randomBetween(-8, 8), 4, 96);
			const angle = clamp(preset.angle + randomBetween(-18, 18), -88, 88);
			const length = clamp(preset.length + randomBetween(-10, 18), 16, 64);
			const opacity = clamp(preset.opacity + randomBetween(-0.12, 0.14), 0.22, 0.82);
			const thickness = index % 4 === 0 ? 2 : 1;

			line.style.setProperty("--x", `${x}%`);
			line.style.setProperty("--y", `${y}%`);
			line.style.setProperty("--angle", `${angle}deg`);
			line.style.setProperty("--length", `${length}vw`);
			line.style.setProperty("--opacity", opacity.toFixed(2));
			line.style.setProperty("--thickness", `${thickness}px`);

			field.appendChild(line);
		}

		document.body.prepend(field);
	};

	if (document.readyState === "loading") {
		document.addEventListener("DOMContentLoaded", buildField, { once: true });
	} else {
		buildField();
	}
})();