from ultralytics import YOLO
import cv2
import time
import pyautogui  # For screen resolution

# Load YOLOv8 model
model = YOLO("yolov8n.pt")

# Define target class (0 = person)
TARGET_CLASS_ID = 0

# Get screen resolution once
screen_width, screen_height = pyautogui.size()
output_resolution = (screen_width, screen_height)

# Start video capture
cap = cv2.VideoCapture(0)

# Optional: Set webcam resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    results = model(frame)

    # Default settings
    direction = "No target detected"
    frame_height = frame.shape[0]
    frame_width = frame.shape[1]
    annotated_frame = frame.copy()

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        if class_id == TARGET_CLASS_ID:
            x_center = int(box.xywh[0][0])
            box_height = int(box.xywh[0][3])

            # Collision check
            if box_height > frame_height * 0.8:
                direction = "STOP - TOO CLOSE!"
                break

            # Direction logic
            if x_center < frame_width / 3:
                direction = "GO LEFT"
            elif x_center > 2 * frame_width / 3:
                direction = "GO RIGHT"
            else:
                direction = "GO FORWARD"

            # Annotate detection
            annotated_frame = results[0].plot()
            cv2.putText(annotated_frame, direction, (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            break

    # If no target found or too close, annotate
    if direction == "No target detected" or "STOP" in direction:
        cv2.putText(annotated_frame, direction, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    # Resize to screen and show fullscreen
    resized_frame = cv2.resize(annotated_frame, output_resolution)
    cv2.namedWindow("Target Tracking with Collision Prevention", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Target Tracking with Collision Prevention", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow("Target Tracking with Collision Prevention", resized_frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
