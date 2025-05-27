import tkinter as tk
import cv2
import mediapipe as mp

# ===== Mediapipe Setup =====
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# ===== Globals =====
cap = None
calibrated_x, calibrated_y = None, None
IRIS_ID = 474  # Right iris center
NOSE_ID = 1    # Nose tip
threshold = 15  # Pixels for eye
head_threshold = 40  # Pixels for head

# ===== Logic =====
def get_direction(x, y, cx, cy, threshold):
    dx = x - cx
    dy = y - cy
    if abs(dx) < threshold and abs(dy) < threshold:
        return "Center"
    elif abs(dx) > abs(dy):
        return "Left" if dx < 0 else "Right"
    else:
        return "Up" if dy < 0 else "Down"

def calibrate(mode, landmarks, w, h):
    global calibrated_x, calibrated_y
    if mode == "eye":
        pt = landmarks.landmark[IRIS_ID]
    else:
        pt = landmarks.landmark[NOSE_ID]
    calibrated_x = int(pt.x * w)
    calibrated_y = int(pt.y * h)
    print(f"[CALIBRATED] {mode} center: ({calibrated_x}, {calibrated_y})")

def start_tracking(mode):
    global calibrated_x, calibrated_y
    calibrated_x = None
    calibrated_y = None

    global cap
    cap = cv2.VideoCapture(0)

    print(f"[INFO] Starting {mode} tracking... Press 'c' to calibrate, ESC to exit.")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            face = results.multi_face_landmarks[0]

            # Use iris or nose point
            if mode == "eye":
                pt = face.landmark[IRIS_ID]
                t = threshold
            else:
                pt = face.landmark[NOSE_ID]
                t = head_threshold

            x = int(pt.x * w)
            y = int(pt.y * h)
            cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            if calibrated_x is not None and calibrated_y is not None:
                direction = get_direction(x, y, calibrated_x, calibrated_y, t)
                cv2.putText(frame, f"Direction: {direction}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                print(f"[{mode.upper()}] {direction}")
            else:
                cv2.putText(frame, "Press 'C' to calibrate", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow(f"{mode.title()} Tracking", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('c'):
            if results.multi_face_landmarks:
                calibrate(mode, results.multi_face_landmarks[0], w, h)

    cap.release()
    cv2.destroyAllWindows()

# ===== GUI =====
def run_gui():
    window = tk.Tk()
    window.title("Select Control Mode")
    window.geometry("600x400")

    tk.Label(window, text="Choose a control method:", font=("Helvetica", 14)).pack(pady=20)

    tk.Button(window, text="🧠 Head Tracking", font=("Helvetica", 12), width=20,
              command=lambda: [window.destroy(), start_tracking("head")]).pack(pady=10)

    tk.Button(window, text="👁️ Eye Tracking", font=("Helvetica", 12), width=20,
              command=lambda: [window.destroy(), start_tracking("eye")]).pack(pady=10)

    tk.Button(window, text="❌ Exit", font=("Helvetica", 12), width=20,
              command=window.destroy).pack(pady=10)

    window.mainloop()

run_gui()
