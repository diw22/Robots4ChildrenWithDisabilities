import cv2
import mediapipe as mp

# MediaPipe face mesh setup
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# Webcam
cap = cv2.VideoCapture(0)

# Calibration center
calibrated_x, calibrated_y = None, None
threshold = 15  # Pixel movement threshold

# Right iris landmark index in MediaPipe
IRIS_ID = 474  # Approximate center of the right iris

def get_direction(eye_x, eye_y):
    dx = eye_x - calibrated_x
    dy = eye_y - calibrated_y

    if abs(dx) < threshold and abs(dy) < threshold:
        return "Center"
    elif abs(dx) > abs(dy):
        return "Left" if dx < 0 else "Right"
    else:
        return "Up" if dy < 0 else "Down"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    img_h, img_w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            iris = face_landmarks.landmark[IRIS_ID]
            iris_x = int(iris.x * img_w)
            iris_y = int(iris.y * img_h)

            cv2.circle(frame, (iris_x, iris_y), 4, (0, 255, 0), -1)

            if calibrated_x is not None and calibrated_y is not None:
                direction = get_direction(iris_x, iris_y)
                cv2.putText(frame, f"Direction: {direction}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                print(f"[EYE CONTROL] {direction}")
            else:
                cv2.putText(frame, "Press 'C' to calibrate gaze center", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

    cv2.imshow("Eye Joystick", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == ord('c'):
        if results.multi_face_landmarks:
            iris = results.multi_face_landmarks[0].landmark[IRIS_ID]
            calibrated_x = int(iris.x * img_w)
            calibrated_y = int(iris.y * img_h)
            print(f"[CALIBRATED] Eye center: ({calibrated_x}, {calibrated_y})")

cap.release()
cv2.destroyAllWindows()
