# 🪞 Smart Mirror

A fullscreen smart mirror dashboard built with Flask and Python, designed to run on a Raspberry Pi 5. Displays the current time, date, weather, a monthly calendar, and upcoming events — with gesture control via a webcam using MediaPipe.

---

## Features

- 🕐 **Live Clock & Date**
- 🌤️ **Real-time Weather** (auto-detects location via IP)
- 📅 **Monthly Calendar**
- 📋 **Upcoming Events** (from a local JSON file)
- ✋ **Gesture Control** — FIST, OPEN_PALM, OK, Swipe Left/Right

---

## Project Structure

```
smart-mirror/
├── app/
│   ├── main.py                  # Flask app entry point
│   ├── modules/
│   │   ├── clock.py             # Time & date widget
│   │   ├── weather.py           # OpenWeatherMap integration
│   │   ├── events.py            # Events loader
│   │   ├── month.py             # Calendar widget
│   │   ├── gestures.py          # Camera loop + MediaPipe gesture detection
│   │   ├── events.json          # Your events data
│   │   └── gesture_state.txt    # Shared state file for gesture IPC
│   └── ui/
│       ├── templates/           # HTML templates (Jinja2)
│       └── static/              # CSS, JS, images
├── .env                         # Your secrets (NOT committed to git)
├── .env.example                 # Template — copy this to .env
├── requirements.txt             # Python dependencies
└── README.md
```

---

## Local Setup (Mac)

### 1. Clone the repo
```bash
git clone <your-repo-url>
cd smart-mirror
```

### 2. Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
```bash
cp .env.example .env
# Open .env and paste your OpenWeatherMap API key
```
Get a free key at [openweathermap.org/api](https://openweathermap.org/api).

### 5. Run the app
```bash
python app/main.py
```
Then open **http://localhost:8000** in your browser.

---

## Raspberry Pi 5 Deployment

### ⚠️ Known Dependency Issues

| Package | Issue | Fix |
|---|---|---|
| `opencv-python` | Needs GUI libs | Use `opencv-python-headless` instead |
| `mediapipe` | No official ARM64 wheel | See note below |

**MediaPipe on Pi 5:** There is no official pip wheel for ARM64. You may need to install a community-built wheel or build from source. Search: *"mediapipe raspberry pi 5 arm64"* for the latest options.

### Pi Setup Steps

**1. Transfer the code** (choose one):
```bash
# Option A — Git
git clone <your-repo-url>

# Option B — SCP from your Mac
scp -r smart-mirror/ pi@<pi-ip>:~/smart-mirror
```

**2. Install dependencies on the Pi:**
```bash
cd smart-mirror
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**3. Set up your `.env`:**
```bash
cp .env.example .env
nano .env   # paste your real API key
```

**4. Run the app:**
```bash
python app/main.py
```

### Autostart on Boot (systemd)

Create `/etc/systemd/system/smart-mirror.service`:
```ini
[Unit]
Description=Smart Mirror
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/smart-mirror
ExecStart=/home/pi/smart-mirror/.venv/bin/python app/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable it:
```bash
sudo systemctl enable smart-mirror
sudo systemctl start smart-mirror
```

### Kiosk Mode (Fullscreen Browser)

Add to your Pi's autostart config:
```bash
chromium-browser --kiosk --noerrdialogs http://localhost:8000
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `WEATHER_API_KEY` | Your OpenWeatherMap API key |

---

## Gesture Reference

| Gesture | Detection |
|---|---|
| `OPEN_PALM` | All 4 fingers extended |
| `FIST` | No fingers extended |
| `OK` | Pinch + middle/ring/pinky up |
| `Swipe Left` | Wrist moves left rapidly |
| `Swipe Right` | Wrist moves right rapidly |
