import tkinter as tk
from tkinter import messagebox
import cv2
import mediapipe as mp
import pygame
import threading
import time

# Morse code to grid coordinates mapping
morse_locations = {
    ".": (0, 0),
    "-": (0, 1),
    "..": (0, 2),
    ".-": (1, 0),
    "-.": (1, 1),
    "--": (1, 2),
    "...": (2, 0),
    "..-": (2, 1),
    ".--": (2, 2)
}

# Global variables
current_input = ""
position_x, position_y = 0, 0

# For Xbox controller
morse_sequence = ""
last_input_time = None
pause_threshold = 5.0  # 5 seconds

# Tkinter GUI for hospital map
class HospitalMap(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hospital Room Map - Robot Position")
        self.geometry("400x450")
        self.canvas = tk.Canvas(self, width=300, height=300, bg="white")
        self.canvas.pack(pady=20)
        self.position_label = tk.Label(self, text=f"Position: ({position_x}, {position_y})", font=("Helvetica", 14))
        self.position_label.pack()
        self.input_label = tk.Label(self, text="Input Morse Code: ", font=("Helvetica", 12))
        self.input_label.pack()
        self.draw_grid()
        self.draw_robot()

    def draw_grid(self):
        size = 100
        for i in range(4):
            self.canvas.create_line(0, i*size, 300, i*size, fill="black")
            self.canvas.create_line(i*size, 0, i*size, 300, fill="black")

    def draw_robot(self):
        self.canvas.delete("robot")
        size = 100
        # invert y so (0,0) is bottom-left
        cx = position_x * size + size // 2
        cy = (2 - position_y) * size + size // 2
        self.canvas.create_oval(cx-15, cy-15, cx+15, cy+15, fill="red", tags="robot")

    def update_position_label(self):
        self.position_label.config(text=f"Position: ({position_x}, {position_y})")

    def update_input_label(self):
        self.input_label.config(text=f"Input Morse Code: {current_input}")

hospital_map = HospitalMap()

def send_to_robot(x, y):
    # Replace with real robot communication
    print(f"[OUTPUT] Sending coordinates to robot: X={x}, Y={y}")

def move_robot_to_location(code):
    global position_x, position_y, current_input
    if code in morse_locations:
        position_x, position_y = morse_locations[code]
        print(f"[MORSE] Moving to '{code}' → Position: ({position_x}, {position_y})")
        hospital_map.draw_robot()
        hospital_map.update_position_label()
        send_to_robot(position_x, position_y)
        current_input = ""
        hospital_map.update_input_label()
    else:
        print(f"[MORSE] Code '{code}' not recognized")

def input_dot():
    global current_input
    current_input += "."
    hospital_map.update_input_label()
    print(f"[INPUT] Dot added: {current_input}")

def input_dash():
    global current_input
    current_input += "-"
    hospital_map.update_input_label()
    print(f"[INPUT] Dash added: {current_input}")

def confirm_input():
    global current_input
    if current_input:
        move_robot_to_location(current_input)

def delete_last_input():
    global current_input
    if current_input:
        current_input = current_input[:-1]
        hospital_map.update_input_label()
        print(f"[INPUT] Deleted last input: {current_input}")

# ------------------------------------------
# Head Tracking Setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
center_x, center_y = None, None
threshold = 40
head_last_direction = None
head_cooldown_time = 0.5
head_last_input_time = 0

def get_direction(nose_x, nose_y, cx, cy, thresh):
    dx = nose_x - cx
    dy = nose_y - cy
    if abs(dx) < thresh and abs(dy) < thresh:
        return "Center"
    if dy < -thresh:
        return "Up"
    elif dy > thresh:
        return "Down"
    if abs(dx) > abs(dy):
        return "Right" if dx > 0 else "Left"
    return "Center"

def get_pupil_center(landmarks, indices, img_w, img_h):
    xs = [landmarks[i].x * img_w for i in indices]
    ys = [landmarks[i].y * img_h for i in indices]
    return int(sum(xs) / len(xs)), int(sum(ys) / len(ys))

def run_head_tracking():
    global center_x, center_y
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[ERROR] Cannot open webcam.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        img_h, img_w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                lm = face_landmarks.landmark

                left_pupil = get_pupil_center(lm, [468, 469, 470, 471], img_w, img_h)
                right_pupil = get_pupil_center(lm, [473, 474, 475, 476], img_w, img_h)
                pupil_dist = abs(left_pupil[0] - right_pupil[0])
                pupil_y_diff = left_pupil[1] - right_pupil[1]

                nose = lm[1]
                nose_x = int(nose.x * img_w)
                nose_y = int(nose.y * img_h)

                cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 0), -1)

                if center_x is not None and center_y is not None:
                    if nose_y < center_y - 40:
                        print("[HEAD] Move Forward")
                    elif nose_y > center_y + 40:
                        print("[HEAD] Move Backward")

                    if nose_y < center_y - 80:
                        print("[HEAD] Elevate Arm")
                    elif nose_y > center_y + 80:
                        print("[HEAD] De-elevate Arm")

                    if pupil_y_diff > 20:
                        print("[HEAD] Rotate Wrist Left")
                    elif pupil_y_diff < -20:
                        print("[HEAD] Rotate Wrist Right")

                    if pupil_dist > 140:
                        print("[HEAD] Neck Move Down")
                    elif pupil_dist < 100:
                        print("[HEAD] Neck Move Up")

        cv2.putText(frame, "Press 'C' to calibrate center", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Head Tracking Arm Control", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key == ord('c'):
            if results.multi_face_landmarks:
                nose = results.multi_face_landmarks[0].landmark[1]
                center_x = int(nose.x * img_w)
                center_y = int(nose.y * img_h)
                print(f"[CALIBRATED] Center: ({center_x}, {center_y})")

    cap.release()
    cv2.destroyAllWindows()

# ------------------------------------------
# Eye Tracking Setup
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
eyes_center_x, eyes_center_y = None, None
eye_threshold = 15
eye_last_direction = None
eye_cooldown_time = 0.5
eye_last_input_time = 0

def get_eye_direction(x, y, cx, cy, thresh):
    dx = x - cx
    dy = y - cy
    if abs(dx) < thresh and abs(dy) < thresh:
        return "Center"
    if dy < -thresh:
        return "Up"
    elif dy > thresh:
        return "Down"
    if abs(dx) > abs(dy):
        return "Right" if dx > 0 else "Left"
    return "Center"

def run_eye_tracking():
    global eyes_center_x, eyes_center_y, eye_last_direction, eye_last_input_time
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape
        eyes = eye_cascade.detectMultiScale(gray, 1.3, 5)

        if len(eyes) > 0:
            (ex, ey, ew, eh) = eyes[0]
            x = ex + ew // 2
            y = ey + eh // 2
            cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            if eyes_center_x is not None:
                direction = get_eye_direction(x, y, eyes_center_x, eyes_center_y, eye_threshold)
                current_time = time.time()
                if direction != eye_last_direction and current_time - eye_last_input_time > eye_cooldown_time:
                    if direction == "Left":
                        input_dot()
                    elif direction == "Right":
                        input_dash()
                    elif direction == "Up":
                        print("[INPUT] Submit detected (eye look up)")
                        confirm_input()
                    elif direction == "Down":
                        print("[INPUT] Delete detected (eye look down)")
                        delete_last_input()
                    eye_last_input_time = current_time
                    eye_last_direction = direction
                elif direction == "Center":
                    eye_last_direction = None

        cv2.putText(frame, "Press 'C' to calibrate eye center", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "Look Left=dot '.' | Right=dash '-' | Up=Submit | Down=Delete", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        cv2.imshow("Eye Tracking Morse Input", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            if len(eyes) > 0:
                (ex, ey, ew, eh) = eyes[0]
                eyes_center_x, eyes_center_y = ex + ew // 2, ey + eh // 2
                print(f"[CALIBRATED] Eye center set to ({eyes_center_x}, {eyes_center_y})")
        elif key == 8:  # Backspace
            delete_last_input()
        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

# ------------------------------------------
# Robot position/state
robot_x, robot_y = 0, 0

# ------------------ ROBOT ARM MOVEMENT ------------------
def move_robot_arm(dx, dy):
    print(f"[ARM] Move dx: {dx:.2f}, dy: {dy:.2f}")

# ------------------ UPDATE COORDINATES ------------------
def update_coordinates_from_morse(sequence):
    global robot_x, robot_y
    coords = morse_locations.get(sequence)
    if coords:
        robot_x, robot_y = coords
        print(f"[ROBOT] Moving to: {coords} from Morse '{sequence}'")
    else:
        print(f"[ROBOT] Invalid Morse code: {sequence}")
def run_xac_controller():
    global morse_sequence, last_input_time

    pygame.init()
    pygame.joystick.init()

    if pygame.joystick.get_count() == 0:
        print("[XAC] No joystick detected.")
        return

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"[XAC] Using: {joystick.get_name()}")

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button as dot
                    morse_sequence += "."
                    last_input_time = time.time()
                    print(f"[XAC] Dot added: {morse_sequence}")
                elif event.button == 1:  # B button as dash
                    morse_sequence += "-"
                    last_input_time = time.time()
                    print(f"[XAC] Dash added: {morse_sequence}")

        # Joystick movement for robot arm
        if joystick.get_numaxes() >= 2:
            dx = joystick.get_axis(0)
            dy = joystick.get_axis(1)
            if abs(dx) > 0.2 or abs(dy) > 0.2:
                move_robot_arm(dx, dy)

        # Check for pause to auto-submit Morse
        if morse_sequence and last_input_time:
            if time.time() - last_input_time > pause_threshold:
                update_coordinates_from_morse(morse_sequence)
                morse_sequence = ""
                last_input_time = None

        clock.tick(30)

# ------------------------------------------
# Input Mode Selection GUI
class InputSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Select Input Method")
        self.geometry("300x200")
        self.selected_mode = tk.StringVar(value="Head Tracking")

        tk.Label(self, text="Select Input Method:", font=("Helvetica", 14)).pack(pady=10)
        tk.Radiobutton(self, text="Head Tracking", variable=self.selected_mode, value="Head Tracking").pack(anchor='w', padx=30)
        tk.Radiobutton(self, text="Eye Tracking", variable=self.selected_mode, value="Eye Tracking").pack(anchor='w', padx=30)
        tk.Radiobutton(self, text="PS5 Controller", variable=self.selected_mode, value="PS5 Controller").pack(anchor='w', padx=30)

        tk.Button(self, text="Start", command=self.start_selected_mode).pack(pady=20)

    def start_selected_mode(self):
        mode = self.selected_mode.get()
        print(f"[MODE] Selected: {mode}")
        self.destroy()

        # Start the chosen input method thread
        if mode == "Head Tracking":
            threading.Thread(target=run_head_tracking, daemon=True).start()
        elif mode == "Eye Tracking":
            threading.Thread(target=run_eye_tracking, daemon=True).start()
        elif mode == "Xbox Controller":
            threading.Thread(target=run_xac_controller, daemon=True).start()

        # Start the hospital map GUI mainloop
        hospital_map.mainloop()

if __name__ == "__main__":
    input_selector = InputSelector()
    input_selector.mainloop()
