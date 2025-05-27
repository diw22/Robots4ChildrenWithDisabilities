import tkinter as tk
import cv2
import mediapipe as mp
import pygame
import threading
import time

# -------------------- SHARED CONFIGURATION --------------------
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
calibrated_x, calibrated_y = None, None
NOSE_ID = 1
eye_threshold = 15
head_threshold = 40
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
                (ex, ey, ew, eh) = eyes[0]
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

# -------------------- PS5 TIC-TAC-TOE CONTROLLER --------------------
def start_tictactoe_gui():
    pygame.init()
    pygame.joystick.init()
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"[INFO] Controller: {joystick.get_name()}")

    root = tk.Tk()
    root.title("PS5 Tic-Tac-Toe Control")
    root.geometry("500x400")

    current_symbol = ""
    awaiting_column = False
    board = [[" "]*3 for _ in range(3)]
    current_player = "X"

    label = tk.Label(root, text="Input: ", font=("Helvetica", 18))
    label.pack(pady=20)
    status = tk.Label(root, text="Waiting for row input...", font=("Helvetica", 16))
    status.pack(pady=10)
    tk.Button(root, text="Exit", command=root.destroy).pack(pady=10)

    def update_gui():
        label.config(text=f"Input: {current_symbol}")
        status.config(text="Column input" if awaiting_column else "Row input")

    def submit_move():
        nonlocal current_symbol, awaiting_column, current_player

        if not awaiting_column:
            status.config(text="Finish column input first!")
            return

        row = current_symbol.count('.') - 1
        col = current_symbol.count('-') - 1
        current_symbol = ""
        awaiting_column = False

        if 0 <= row < 3 and 0 <= col < 3:
            if board[row][col] == " ":
                board[row][col] = current_player
                print(f"[MOVE] {current_player} → ({row+1},{col+1})")
                status.config(text=f"Player {current_player} moved to ({row+1},{col+1})")
                label.config(text="\n".join([" ".join(r) for r in board]))
                current_player = "O" if current_player == "X" else "X"
            else:
                status.config(text="Cell already occupied!")
        else:
            status.config(text="Invalid move!")

    def controller_listener():
        nonlocal current_symbol, awaiting_column
        while True:
            pygame.event.pump()
            if joystick.get_button(1):  # Circle → dot
                current_symbol += '.'
                update_gui()
                time.sleep(0.3)
            elif joystick.get_button(2):  # Square → dash
                current_symbol += '-'
                update_gui()
                time.sleep(0.3)
            elif joystick.get_button(0):  # Cross → end of row, start column
                if not awaiting_column:
                    awaiting_column = True
                    update_gui()
                else:
                    status.config(text="Already input row!")
                time.sleep(0.3)
            elif joystick.get_button(11):  # D-Pad Up → submit move
                submit_move()
                time.sleep(0.3)
            elif joystick.get_button(3):  # Triangle → exit
                print("[INFO] Exiting via Triangle")
                root.quit()
                break
            time.sleep(0.05)

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

    tk.Button(menu, text="PS5 Tic-Tac-Toe", font=("Helvetica", 12), width=20,
              command=lambda: [menu.destroy(), start_tictactoe_gui()]).pack(pady=10)

    tk.Button(menu, text="Exit", font=("Helvetica", 12), width=20,
              command=menu.destroy).pack(pady=10)

    menu.mainloop()

run_main_menu()
