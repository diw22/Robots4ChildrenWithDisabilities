import cv2
import mediapipe as mp
import time

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("[ERROR] Could not open webcam.")
    exit()

print("[INFO] Webcam initialized. Press 'C' to calibrate. ESC to quit.")

center_x, center_y = None, None
threshold = 40
morse_mode = False
morse_buffer = ""

morse_input_delay = 0.5  # seconds
last_morse_time = 0

def get_direction(nose_x, nose_y):
    dx = nose_x - center_x
    dy = nose_y - center_y
    print(f"[DEBUG] dx: {dx}, dy: {dy}")
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
            print(f"[SKIP] Ignored {direction} due to delay")
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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to read from webcam.")
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
            print(f"[DEBUG] Left pupil Y: {left_pupil[1]}, Right pupil Y: {right_pupil[1]}")

            if left_pupil[1] < right_pupil[1] - 30:
                morse_mode = False
            elif right_pupil[1] < left_pupil[1] - 30:
                morse_mode = True
            print(f"[MODE] {'Morse' if morse_mode else 'Joystick'}")

            nose = lm[1]
            nose_x = int(nose.x * img_w)
            nose_y = int(nose.y * img_h)
            cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 0), -1)
            print(f"[DEBUG] Nose at ({nose_x}, {nose_y})")

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

    else:
        print("[DEBUG] No face detected.")

    mode_text = "Morse Mode" if morse_mode else "Joystick Mode"
    cv2.putText(frame, mode_text, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Head Tracking Joystick + Morse", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        print("[INFO] Exiting...")
        break
    elif key == ord('c'):
        if results.multi_face_landmarks:
            nose = results.multi_face_landmarks[0].landmark[1]
            center_x = int(nose.x * img_w)
            center_y = int(nose.y * img_h)
            print(f"[CALIBRATED] Center set to: ({center_x}, {center_y})")

cap.release()
cv2.destroyAllWindows()
