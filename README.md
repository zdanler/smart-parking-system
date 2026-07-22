# 🚗 Smart Parking Prototype

A real-time app that watches a parking lot through your webcam and tells you which spots are **free** or **taken** using AI object detection. It's built as a simple learning project for combining computer vision (YOLOv8) with an interactive web dashboard (Streamlit).

---

## ✨ Key Features

- 🎥 **Live webcam monitoring** — captures video frames directly from your Mac's camera.
- 🤖 **AI-powered car detection** using the YOLOv8 model (pretrained, no training required).
- 🟩🟥 **Visual slot status** — draws green boxes for available spots and red boxes for occupied ones directly on the video.
- 📊 **Two dashboard views**:
  - **Admin Dashboard** — live feed, detection details, and metrics (great for debugging).
  - **Student View** — a simple, color-coded summary anyone can glance at.
- ▶️ **Start/Stop controls** to turn the camera on and off safely.
- ⚙️ **Easy to customize** — slot positions and detection sensitivity are simple variables you can tweak.

---

## 🧰 Tech Stack

| Type | Tool |
|---|---|
| Language | Python |
| Web Dashboard | Streamlit |
| Computer Vision | OpenCV |
| AI Model | YOLOv8 (via Ultralytics) |
| Model Weights | `yolov8s.pt` |

---

## 📦 Prerequisites & Installation

**Before you start, make sure you have:**
- Python 3.9 or newer installed
- A working webcam
- A Mac (the camera setup is configured for macOS by default)

### Step 1 — Get the project files

```bash
git clone <your-repository-url>
cd <your-project-folder>
```

### Step 2 — (Recommended) Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install the required libraries

```bash
pip install streamlit opencv-python ultralytics
```

### Step 4 — Get the YOLOv8 model file

The app needs a file called `yolov8s.pt` (the AI model weights). If you don't already have it, run this once to download it:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
```

Then place `yolov8s.pt` in your **project folder** (or your Desktop — the app automatically searches both).

---

## 🚀 How to Run (Quick Start)

1. Open your terminal in the project folder.
2. Run the app with:

```bash
streamlit run main.py
```

3. Your browser will open automatically (usually at `http://localhost:8501`).
4. Click **"Start Camera"** to begin detecting cars.
5. Switch between the **Admin Dashboard** and **Student View** tabs to see the results.
6. Click **"Stop Camera"** when you're done — this releases your webcam properly.

---

## ⚙️ Important Variables / Configuration

All the settings you might want to tweak are near the top of `main.py`:

| Variable | What it does | Default |
|---|---|---|
| `CAMERA_INDEX` | Which webcam to use (change if you have more than one camera) | `0` |
| `CONF_THRESHOLD` | How confident the AI must be before counting something as a car (lower = more detections, but less accurate) | `0.35` |
| `OVERLAP_THRESHOLD` | How much a car must overlap a parking slot to count it as "occupied" | `0.15` |
| `FRAME_DELAY_SECONDS` | Delay between each frame update (controls how fast the video refreshes) | `0.05` |
| `PARKING_SLOTS` | The list of parking spot positions on screen (as percentages of the frame, not pixels) | 3 example slots |

### Customizing parking slot positions

Each slot is written as `(x1, y1, x2, y2)`, where all values are between `0` and `1` (think of it as a percentage of the screen width/height). For example:

```python
PARKING_SLOTS = [
    (0.05, 0.55, 0.30, 0.95),  # Slot 1 — bottom-left area
    (0.35, 0.55, 0.60, 0.95),  # Slot 2 — bottom-middle area
    (0.65, 0.55, 0.95, 0.95),  # Slot 3 — bottom-right area
]
```

👉 To add more slots or reposition existing ones, just edit or add more tuples to this list to match where the parking spaces actually appear in your camera view.

---

## ✅ Expected Output

When everything is working correctly, you should see:

- A **browser window** opens showing the "Smart Parking Prototype" dashboard.
- After clicking **Start Camera**, your webcam feed appears with colored boxes overlaid on it:
  - 🟩 **Green box + "Available"** label = empty parking slot
  - 🟥 **Red box + "Occupied"** label = a car is parked there
  - 🟧 Thin orange boxes = individual car detections with confidence scores (e.g., `car 0.87`)
- The **Admin Dashboard** tab shows live metrics (how many slots are open/occupied) and a list of raw detections.
- The **Student View** tab shows a simple, color-coded summary (green = available, red = full) that updates automatically.
- Clicking **Stop Camera** turns off the webcam and resets everything back to "Offline."

If the camera doesn't open or a frame can't be read, you'll see a clear warning/error message in the app instead of a crash.
