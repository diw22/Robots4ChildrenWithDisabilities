import tkinter as tk               # Used for the menu and GUI interfaces
import cv2                         # For capturing and displaying webcam video
import mediapipe as mp             # Tracks facial landmarks for head tracking
import pygame                      # Interfaces with the PS5 controller
import threading                   # Allows concurrent execution (e.g. controller input)
import time                        # Used for timing/delays in button response

# -------------------- SHARED CONFIGURATION --------------------
# Initialise MediaPipe's FaceMesh solution for head tracking
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# Global variables to hold the calibrated central position
calibrated_x, calibrated_y = None, None

# Landmark index from MediaPipe for head tracking
NOSE_ID = 1     # Nose tip for head tracking

# Thresholds for movement sensitivity
eye_threshold = 15      # Smaller threshold: for subtle eye movement
head_threshold = 40     # Larger threshold: for broader head movement

# Load Haar cascade for eye detection
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# -------------------- HEAD/EYE TRACKING FUNCTIONS --------------------

def get_direction(x, y, cx, cy, threshold):
    dx = x - cx
    dy = y - cy
    if abs(dx) < threshold and abs(dy) < threshold:
        return "Centre"
    elif abs(dx) > abs(dy):
        return "Left" if dx < 0 else "Right"
    else:
        return "Up" if dy < 0 else "Down"

def calibrate(mode, x, y):
    global calibrated_x, calibrated_y
    calibrated_x = x
    calibrated_y = y
    print(f"[CALIBRATED] {mode} centre: ({calibrated_x}, {calibrated_y})")

def start_tracking(mode):
    global calibrated_x, calibrated_y
    calibrated_x = None
    calibrated_y = None

    cap = cv2.VideoCapture(0)
    print(f"[INFO] Starting {mode} tracking... Press 'c' to calibrate, ESC to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if mode == "eye":
            eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)
            if len(eyes) > 0:
                (ex, ey, ew, eh) = eyes[0]  # Use the first detected eye
                x = ex + ew // 2
                y = ey + eh // 2
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

                if calibrated_x is not None:
                    direction = get_direction(x, y, calibrated_x, calibrated_y, eye_threshold)
                    cv2.putText(frame, f"Direction: {direction}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    print(f"[EYE] {direction}")
                else:
                    cv2.putText(frame, "Press 'C' to calibrate", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        elif mode == "head":
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                face = results.multi_face_landmarks[0]
                pt = face.landmark[NOSE_ID]
                x = int(pt.x * w)
                y = int(pt.y * h)
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

                if calibrated_x is not None:
                    direction = get_direction(x, y, calibrated_x, calibrated_y, head_threshold)
                    cv2.putText(frame, f"Direction: {direction}", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    print(f"[HEAD] {direction}")
                else:
                    cv2.putText(frame, "Press 'C' to calibrate", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow(f"{mode.title()} Tracking", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break
        elif key == ord('c'):
            if mode == "eye" and len(eyes) > 0:
                calibrate(mode, x, y)
            elif mode == "head" and results.multi_face_landmarks:
                calibrate(mode, x, y)

    cap.release()
    cv2.destroyAllWindows()

# -------------------- CONTROLLER MORSE CODE MODE --------------------

def start_controller_gui():
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"[INFO] Controller: {joystick.get_name()}")

    root = tk.Tk()
    root.title("PS5 Morse + D-Pad Control")
    root.geometry("500x350")

    morse_input = ""
    label = tk.Label(root, text="Morse Code: ", font=("Helvetica", 20))
    label.pack(pady=20)
    status = tk.Label(root, text="Waiting for input...", font=("Helvetica", 16))
    status.pack(pady=10)
    tk.Button(root, text="Exit", command=root.destroy).pack(pady=10)

    morse_command_map = {
        '.': "Wave", '-': "Fetch Toy", '.-': "Play Music",
        '--': "Rest Pose", '..': "Clap", '-.': "Spin Around"
    }

    def update_gui():
        label.config(text=f"Morse Code: {morse_input}")
        status.config(text="Typing...")

    def submit_command():
        nonlocal morse_input
        command = morse_command_map.get(morse_input.strip(), "Unknown Command")
        status.config(text=f"Action: {command}")
        label.config(text=f"Executed: {command}")
        print(f"[INFO] Morse '{morse_input}' → {command}")
        morse_input = ""

    def handle_dpad(x, y):
        if (x, y) == (0, 1): action = "Move Forward"
        elif (x, y) == (0, -1): action = "Move Backward"
        elif (x, y) == (-1, 0): action = "Turn Left"
        elif (x, y) == (1, 0): action = "Turn Right"
        else: return
        status.config(text=f"D-Pad: {action}")
        label.config(text=f"Manual Control: {action}")
        print(f"[D-PAD] {action}")

    def controller_listener():
        nonlocal morse_input
        while True:
            pygame.event.pump()
            if joystick.get_button(0):
                if morse_input:
                    morse_input = morse_input[:-1]
                    update_gui()
                time.sleep(0.3)
            elif joystick.get_button(2):
                morse_input += '-'
                update_gui()
                time.sleep(0.3)
            elif joystick.get_button(1):
                morse_input += '.'
                update_gui()
                time.sleep(0.3)
            elif joystick.get_button(9):
                submit_command()
                time.sleep(0.3)
            elif joystick.get_button(3):
                print("[INFO] Exiting via Triangle")
                root.quit()
                break
            elif joystick.get_button(11): handle_dpad(0, 1)
            elif joystick.get_button(12): handle_dpad(0, -1)
            elif joystick.get_button(13): handle_dpad(-1, 0)
            elif joystick.get_button(14): handle_dpad(1, 0)
            time.sleep(0.05)

    root.bind("<KeyPress>", lambda event: None)
    threading.Thread(target=controller_listener, daemon=True).start()
    root.mainloop()

# -------------------- MAIN MENU --------------------

def run_main_menu():
    menu = tk.Tk()
    menu.title("Select Input Mode")
    menu.geometry("450x300")

    tk.Label(menu, text="Choose Control Mode:", font=("Helvetica", 14)).pack(pady=20)

    tk.Button(menu, text="Head Tracking", font=("Helvetica", 12), width=20,
              command=lambda: [menu.destroy(), start_tracking("head")]).pack(pady=10)

    tk.Button(menu, text="Eye Tracking", font=("Helvetica", 12), width=20,
              command=lambda: [menu.destroy(), start_tracking("eye")]).pack(pady=10)

    tk.Button(menu, text="PS5 Morse Controller", font=("Helvetica", 12), width=20,
              command=lambda: [menu.destroy(), start_controller_gui()]).pack(pady=10)

    tk.Button(menu, text="Exit", font=("Helvetica", 12), width=20,
              command=menu.destroy).pack(pady=10)

    menu.mainloop()

run_main_menu()
