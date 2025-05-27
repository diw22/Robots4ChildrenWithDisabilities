import cv2
import numpy as np

# Start video capture from the default webcam
cap = cv2.VideoCapture(0)

# Check if the webcam is accessible
if not cap.isOpened():
    print("Webcam not accessible")
    exit()

# This represents the center of the frame (assuming 640x480 resolution)
frame_center = 320

print("Looking for a red ball... Press 'q' to quit.")

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame to a standard size (640x480)
    frame = cv2.resize(frame, (640, 480))

    # Convert the frame from BGR (OpenCV default) to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define two HSV ranges for the color red (since red wraps around 0 degrees)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([179, 255, 255])

    # Create masks for the two red ranges
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

    # Combine the two masks into one
    mask = cv2.bitwise_or(mask1, mask2)

    # Find contours (edges) in the masked image
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Default direction output
    direction = "No ball detected"

    if contours:
        # Find the largest contour (assuming it's the ball)
        c = max(contours, key=cv2.contourArea)

        # Find the minimum enclosing circle around the contour
        ((x, y), radius) = cv2.minEnclosingCircle(c)

        # Only proceed if the detected object is large enough to be a real ball
        if radius > 10:
            # Decide direction based on ball's horizontal position
            if x < frame_center - 50:
                direction = "Move Left"
            elif x > frame_center + 50:
                direction = "Move Right"
            else:
                direction = "Move Forward"

    # Print the direction in the terminal, updating on the same line
    print(f"Direction: {direction}", end='\r')

    # Optional: Show webcam feed with ball and debug info
    cv2.imshow("Webcam Feed", frame)

    # Break the loop if the user presses 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
