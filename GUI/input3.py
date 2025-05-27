import tkinter as tk
import cv2
import mediapipe as mp
import pygame
import threading
import time

# -------------------- HEAD TRACKING + MORSE INTEGRATED --------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

center_x, center_y = None, None
threshold = 40
morse_mode = False
morse_buffer = ""

morse_input_delay = 0.5
last_morse_time = 0

def get_direction(nose_x, nose_y):
    dx = nose_x - center_x
    dy = nose_y - center_y
    if abs(dx) < threshold and abs(dy) < threshold:
        return "Center"
    elif abs(dx) > abs(dy):
        return "Right" if dx < 0 else "Left"
    else:
        return "Up" if dy < 0 else "Down"

def handle_morse(direction):
    global morse_buffer, last_morse_time
    current_time = time.time()
    if direction in ["Left", "Right"]:
        if current_time - last_morse_time < morse_input_delay:
            return
        last_morse_time = current_time
    if direction == "Left":
        morse_buffer += "."
    elif direction == "Right":
        morse_buffer += "-"
    elif direction == "Up":
        print(f"[MORSE SUBMIT] {morse_buffer}")
        morse_buffer = ""
    elif direction == "Down":
        morse_buffer = morse_buffer[:-1]
    print(f"[MORSE BUFFER] {morse_buffer}") 

def get_pupil_center(landmarks, indices, img_w, img_h):
    xs = [landmarks[i].x * img_w for i in indices]
    ys = [landmarks[i].y * img_h for i in indices]
    return int(sum(xs) / len(xs)), int(sum(ys) / len(ys))

def run_head_tracking():
    global center_x, center_y, morse_mode
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
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

                cv2.circle(frame, left_pupil, 3, (0, 255, 255), -1)
                cv2.circle(frame, right_pupil, 3, (255, 255, 0), -1)

                if left_pupil[1] < right_pupil[1] - 30:
                    morse_mode = False
                elif right_pupil[1] < left_pupil[1] - 30:
                    morse_mode = True

                nose = lm[1]
                nose_x = int(nose.x * img_w)
                nose_y = int(nose.y * img_h)
                cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 0), -1)

                if center_x is not None and center_y is not None:
                    direction = get_direction(nose_x, nose_y)
                    if morse_mode:
                        handle_morse(direction)
                        cv2.putText(frame, f"Morse: {morse_buffer}", (10, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                    else:
                        cv2.putText(frame, f"Direction: {direction}", (10, 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        print(f"[HEAD] {direction}")
                else:
                    cv2.putText(frame, "Press 'C' to calibrate center", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        mode_text = "Morse Mode" if morse_mode else "Joystick Mode"
        cv2.putText(frame, mode_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Head Tracking Joystick + Morse", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key == ord('c'):
            if results.multi_face_landmarks:
                nose = results.multi_face_landmarks[0].landmark[1]
                center_x = int(nose.x * img_w)
                center_y = int(nose.y * img_h)
                print(f"[CALIBRATED] Center set to: ({center_x}, {center_y})")

    cap.release()
    cv2.destroyAllWindows()

# -------------------- EYE TRACKING --------------------
eye_threshold = 15
eyes_center_x, eyes_center_y = None, None
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def run_eye_tracking():
    global eyes_center_x, eyes_center_y
    eyes_center_x, eyes_center_y = None, None

    cap = cv2.VideoCapture(0)
    print("[INFO] Starting eye tracking... Press 'c' to calibrate, ESC to exit.")

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
                direction = get_direction(x, y, eyes_center_x, eyes_center_y, eye_threshold)
                cv2.putText(frame, f"Direction: {direction}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                print(f"[EYE] {direction}")
            else:
                cv2.putText(frame, "Press 'C' to calibrate", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Eye Tracking", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break
        elif key == ord('c') and len(eyes) > 0:
            eyes_center_x = x
            eyes_center_y = y
            print(f"[CALIBRATED] Eye center set to: ({eyes_center_x}, {eyes_center_y})")

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
    menu.geometry("450x350")

    tk.Label(menu, text="Choose Control Mode:", font=("Helvetica", 14)).pack(pady=20)

    tk.Button(menu, text="Head Tracking", font=("Helvetica", 12), width=25,
              command=lambda: [menu.destroy(), run_head_tracking()]).pack(pady=10)

    tk.Button(menu, text="Eye Tracking", font=("Helvetica", 12), width=25,
              command=lambda: [menu.destroy(), run_eye_tracking()]).pack(pady=10)

    tk.Button(menu, text="PS5 Controller", font=("Helvetica", 12), width=25,
              command=lambda: [menu.destroy(), start_controller_gui()]).pack(pady=10)

    tk.Button(menu, text="Exit", font=("Helvetica", 12), width=25,
              command=menu.destroy).pack(pady=10)

    menu.mainloop()

if __name__ == "__main__":
    run_main_menu()