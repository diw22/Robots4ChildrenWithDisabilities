# Import necessary libraries
from ultralytics import YOLO  # type: ignore # YOLOv8 for object detection
import cv2  # OpenCV for image capture and display

# Load the pretrained YOLOv8 model (nano version - fast and lightweight)
model = YOLO("yolov8n.pt")

# Set the target object class (based on COCO class IDs)
# You can change this to another class, like 41 for 'cup' or 32 for 'sports ball'
TARGET_CLASS_ID = 0  # 0 corresponds to 'person' in the COCO dataset (https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml)

# Initialize the webcam for real-time video capture
cap = cv2.VideoCapture(0)  # 0 is typically the default webcam

# Main loop for continuously capturing frames and performing detection
while True:
    ret, frame = cap.read()  # Read a frame from the webcam
    if not ret:
        break  # If frame capture fails, exit the loop

    # Run YOLO object detection on the current frame
    results = model(frame)

    # Initialize the default direction output
    direction = "No target detected"

    # Loop through all detected objects (bounding boxes) in the frame
    for box in results[0].boxes:
        class_id = int(box.cls[0])  # Get the detected class ID
        if class_id == TARGET_CLASS_ID:  # Check if it matches the target (e.g., person)
            # Get the x-center coordinate of the bounding box
            x_center = int(box.xywh[0][0])
            width = frame.shape[1]  # Get the width of the frame

            # Determine which direction to move based on where the object is  (LATER ON WE IMPLEMENT THIS WITH THE ROBOT MOVEMENT)
            if x_center < width / 3:
                direction = "GO LEFT"
            elif x_center > 2 * width / 3:
                direction = "GO RIGHT"
            else:
                direction = "GO FORWARD"

            # Annotate the frame with bounding boxes and direction label
            annotated_frame = results[0].plot()
            cv2.putText(annotated_frame, direction, (20, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            break  # Stop after processing the first matching object
    else:
        # If no target object is detected, display default message
        annotated_frame = frame
        cv2.putText(annotated_frame, direction, (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    # Show the annotated video frame in a window
    cv2.imshow("Target Tracking", annotated_frame)

    # Exit the loop when 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
