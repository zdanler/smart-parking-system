"""Smart parking prototype using OpenCV, YOLOv8, and Streamlit."""

from __future__ import annotations

import time
from pathlib import Path

import cv2
import streamlit as st
from ultralytics import YOLO


def resolve_model_path() -> str:
    """Resolve the local YOLO weights file from common project locations."""
    script_dir = Path(__file__).resolve().parent
    parent_roots = list(script_dir.parents)[:3]
    search_roots = [script_dir, *parent_roots, Path.cwd()]

    for root in search_roots:
        candidate = root / "yolov8s.pt"
        if candidate.exists():
            return str(candidate)

        desktop_candidate = root / "Desktop" / "yolov8s.pt"
        if desktop_candidate.exists():
            return str(desktop_candidate)

    return str((Path.cwd() / "yolov8s.pt"))


# COCO class index for "car"
CAR_CLASS_ID = 2
CAMERA_INDEX = 0
MODEL_PATH = resolve_model_path()
CONF_THRESHOLD = 0.35
OVERLAP_THRESHOLD = 0.15
FRAME_DELAY_SECONDS = 0.05

# Normalized parking slot regions: (x1, y1, x2, y2) as fractions of frame size
PARKING_SLOTS = [
    (0.05, 0.55, 0.30, 0.95),
    (0.35, 0.55, 0.60, 0.95),
    (0.65, 0.55, 0.95, 0.95),
]


@st.cache_resource
def load_model() -> YOLO:
    """Load and cache the YOLOv8 small model."""
    return YOLO(MODEL_PATH)


def open_camera() -> cv2.VideoCapture:
    """Open the default Mac webcam."""
    cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_AVFOUNDATION)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return cap


def to_pixel_roi(roi: tuple[float, float, float, float], width: int, height: int) -> tuple[int, int, int, int]:
    """Convert normalized ROI coordinates to pixel coordinates."""
    x1, y1, x2, y2 = roi
    return int(x1 * width), int(y1 * height), int(x2 * width), int(y2 * height)


def detect_cars(model: YOLO, frame) -> list[tuple[int, int, int, int, float]]:
    """Return car bounding boxes as (x1, y1, x2, y2, confidence)."""
    results = model.predict(
        frame,
        conf=CONF_THRESHOLD,
        classes=[CAR_CLASS_ID],
        verbose=False,
    )[0]
    cars: list[tuple[int, int, int, int, float]] = []

    for box in results.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        confidence = float(box.conf[0])
        cars.append((x1, y1, x2, y2, confidence))

    return cars


def overlap_ratio(roi: tuple[int, int, int, int], detection: tuple[int, int, int, int, float]) -> float:
    """Return the fraction of the ROI covered by a detection box."""
    rx1, ry1, rx2, ry2 = roi
    dx1, dy1, dx2, dy2 = detection[:4]

    ix1, iy1 = max(rx1, dx1), max(ry1, dy1)
    ix2, iy2 = min(rx2, dx2), min(ry2, dy2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0

    intersection = (ix2 - ix1) * (iy2 - iy1)
    roi_area = (rx2 - rx1) * (ry2 - ry1)
    return intersection / roi_area if roi_area else 0.0


def slot_is_occupied(roi: tuple[int, int, int, int], cars: list[tuple[int, int, int, int, float]]) -> bool:
    """Determine whether a parking slot contains a car."""
    return any(overlap_ratio(roi, car) >= OVERLAP_THRESHOLD for car in cars)


def draw_slot(frame, roi: tuple[int, int, int, int], occupied: bool) -> None:
    """Draw a parking slot status box and label on the frame."""
    x1, y1, x2, y2 = roi
    color = (0, 0, 255) if occupied else (0, 255, 0)
    label = "Occupied" if occupied else "Available"

    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

    (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv2.rectangle(frame, (x1, y1 - text_height - 12), (x1 + text_width + 12, y1), color, -1)
    cv2.putText(frame, label, (x1 + 6, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)


def draw_car_detections(frame, cars: list[tuple[int, int, int, int, float]]) -> None:
    """Draw lightweight boxes around detected cars."""
    for x1, y1, x2, y2, confidence in cars:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 1)
        cv2.putText(
            frame,
            f"car {confidence:.2f}",
            (x1, max(y1 - 8, 0)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 165, 255),
            1,
        )


def process_frame(
    frame,
    model: YOLO,
) -> tuple[object, int, int, list[dict[str, object]], list[tuple[int, int, int, int, float]]]:
    """Run detection and annotate parking slots on a single frame."""
    height, width = frame.shape[:2]
    cars = detect_cars(model, frame)

    available = 0
    occupied = 0
    slot_statuses: list[dict[str, object]] = []

    for index, slot in enumerate(PARKING_SLOTS, start=1):
        roi = to_pixel_roi(slot, width, height)
        is_occupied = slot_is_occupied(roi, cars)
        draw_slot(frame, roi, is_occupied)
        slot_statuses.append(
            {
                "slot_id": index,
                "occupied": is_occupied,
                "label": "Occupied" if is_occupied else "Available",
            }
        )

        if is_occupied:
            occupied += 1
        else:
            available += 1

    draw_car_detections(frame, cars)
    return frame, available, occupied, slot_statuses, cars


def init_session_state() -> None:
    """Initialize Streamlit session state."""
    defaults = {
        "running": False,
        "camera": None,
        "available_count": 0,
        "occupied_count": 0,
        "slot_statuses": [
            {"slot_id": index, "occupied": False, "label": "Available"}
            for index in range(1, len(PARKING_SLOTS) + 1)
        ],
        "detected_cars": [],
        "rgb_frame": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def start_camera() -> None:
    """Start webcam capture."""
    if st.session_state.running:
        return

    camera = open_camera()
    if not camera.isOpened():
        st.error("Could not open webcam at camera index 0.")
        return

    st.session_state.camera = camera
    st.session_state.running = True


def stop_camera() -> None:
    """Stop webcam capture and release resources."""
    st.session_state.running = False
    camera = st.session_state.camera
    if camera is not None:
        camera.release()
    st.session_state.camera = None
    st.session_state.rgb_frame = None
    st.session_state.detected_cars = []
    st.session_state.slot_statuses = [
        {"slot_id": index, "occupied": False, "label": "Available"}
        for index in range(1, len(PARKING_SLOTS) + 1)
    ]
    st.session_state.available_count = 0
    st.session_state.occupied_count = 0


def get_overall_status() -> str:
    """Return a shared parking summary label for both tabs."""
    if not st.session_state.running:
        return "Offline"

    available = st.session_state.available_count
    total = len(PARKING_SLOTS)

    if available == total:
        return "Available"
    if available == 0:
        return "Full"
    return "Partially Available"


def update_parking_state(model: YOLO) -> None:
    """Capture one frame and refresh shared parking state."""
    camera = st.session_state.camera
    if camera is None or not camera.isOpened():
        st.warning("Webcam is not available.")
        stop_camera()
        return

    ok, frame = camera.read()
    if not ok:
        st.warning("Failed to read a frame from the webcam.")
        stop_camera()
        return

    try:
        annotated_frame, available, occupied, slot_statuses, cars = process_frame(frame.copy(), model)
    except Exception as exc:
        st.error(f"Frame processing failed: {exc}")
        time.sleep(FRAME_DELAY_SECONDS)
        st.rerun()
        return

    st.session_state.available_count = available
    st.session_state.occupied_count = occupied
    st.session_state.slot_statuses = slot_statuses
    st.session_state.detected_cars = cars
    st.session_state.rgb_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)


def render_slot_indicator(slot: dict[str, object]) -> None:
    """Render a large colored slot card for the student view."""
    occupied = bool(slot["occupied"])
    slot_id = slot["slot_id"]
    label = slot["label"]
    background = "#dc3545" if occupied else "#28a745"

    st.markdown(
        f"""
        <div style="
            background-color: {background};
            border-radius: 16px;
            padding: 36px 20px;
            text-align: center;
            min-height: 180px;
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
        ">
            <p style="color: white; font-size: 18px; margin: 0 0 8px 0; opacity: 0.9;">Slot {slot_id}</p>
            <h2 style="color: white; margin: 0; font-size: 34px;">{label}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_admin_dashboard() -> None:
    """Render camera feed, raw detections, and detailed metrics."""
    st.subheader("Detailed Metrics")

    available_col, occupied_col, total_col = st.columns(3)
    available_col.metric("Available", st.session_state.available_count)
    occupied_col.metric("Occupied", st.session_state.occupied_count)
    total_col.metric("Total Slots", len(PARKING_SLOTS))

    st.caption(f"Overall status: **{get_overall_status()}**")

    st.subheader("Live Feed")
    if st.session_state.running and st.session_state.rgb_frame is not None:
        st.image(st.session_state.rgb_frame, channels="RGB", use_container_width=True)
    else:
        st.info("Start the camera to view the live parking feed.")

    st.subheader("Raw Detections")
    cars = st.session_state.detected_cars
    if cars:
        for index, (x1, y1, x2, y2, confidence) in enumerate(cars, start=1):
            st.write(
                f"**Car {index}** — bbox: ({x1}, {y1}) to ({x2}, {y2}) | "
                f"confidence: {confidence:.1%}"
            )
    else:
        st.caption("No cars detected in the current frame.")


def render_student_view() -> None:
    """Render a lightweight student-facing parking summary."""
    status = get_overall_status()

    if status == "Available":
        st.success(f"## Parking is currently: {status}")
    elif status == "Full":
        st.error(f"## Parking is currently: {status}")
    elif status == "Partially Available":
        st.warning(f"## Parking is currently: {status}")
    else:
        st.info("## Parking is currently: Offline")

    summary_col1, summary_col2 = st.columns(2)
    summary_col1.metric("Open Slots", st.session_state.available_count)
    summary_col2.metric("Taken Slots", st.session_state.occupied_count)

    st.subheader("Slot Status")
    slot_columns = st.columns(len(PARKING_SLOTS))
    for column, slot in zip(slot_columns, st.session_state.slot_statuses):
        with column:
            render_slot_indicator(slot)


def main() -> None:
    """Build the Streamlit dashboard."""
    st.set_page_config(page_title="Smart Parking", page_icon="P", layout="wide")

    st.title("Smart Parking Prototype")
    st.caption("Live parking occupancy detection with YOLOv8 and your Mac webcam")

    init_session_state()
    model = load_model()

    control_col, status_col = st.columns([2, 4])
    with control_col:
        start_clicked = st.button("Start Camera", type="primary", disabled=st.session_state.running)
        stop_clicked = st.button("Stop Camera", disabled=not st.session_state.running)

    with status_col:
        if st.session_state.running:
            st.success("Camera is running.")
        else:
            st.info("Click Start Camera to begin monitoring parking slots.")

    if start_clicked:
        start_camera()
    if stop_clicked:
        stop_camera()

    if st.session_state.running:
        update_parking_state(model)

    admin_tab, student_tab = st.tabs(["Admin Dashboard", "Student View"])

    with admin_tab:
        render_admin_dashboard()

    with student_tab:
        render_student_view()

    if st.session_state.running:
        time.sleep(FRAME_DELAY_SECONDS)
        st.rerun()


if __name__ == "__main__":
    main()
