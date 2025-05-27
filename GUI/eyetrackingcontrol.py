import cv2
import mediapipe as mp # type: ignore
import numpy as np

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_faces=1
)

# Camera setup
cap = cv2.VideoCapture(0)  # Use laptop camera

# Define eye landmarks
LEFT_EYE = [362, 263, 249, 390]  # Left eye landmarks
RIGHT_EYE = [33, 7, 163, 144]    # Right eye landmarks

def draw_direction(frame, direction):
    h, w = frame.shape[:2]
    
    # Draw direction indicator
    if direction == "left":
        cv2.arrowedLine(frame, (w-100, h//2), (w-200, h//2), (0,0,255), 5)
    elif direction == "right":
        cv2.arrowedLine(frame, (100, h//2), (200, h//2), (0,0,255), 5)
    else:
        cv2.circle(frame, (w//2, h//2), 30, (0,255,0), -1)
    
    # Add text label
    cv2.putText(frame, f"Looking: {direction}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)

def get_gaze_direction(frame, landmarks):
    # Get eye positions
    left_eye = [landmarks[idx] for idx in LEFT_EYE]
    right_eye = [landmarks[idx] for idx in RIGHT_EYE]
    
    # Calculate eye centers
    left_center = np.mean(left_eye, axis=0).astype(int)
    right_center = np.mean(right_eye, axis=0).astype(int)
    
    # Find gaze midpoint
    gaze_point = ((left_center[0] + right_center[0]) // 2, 
                  (left_center[1] + right_center[1]) // 2)
    
    # Determine direction
    frame_center = frame.shape[1] // 2
    if gaze_point[0] < frame_center - 50:
        return "left"
    elif gaze_point[0] > frame_center + 50:
        return "right"
    else:
        return "center"

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Flip frame horizontally
    frame = cv2.flip(frame, 1)
    
    # Process with MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    direction = "none"
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        h, w, _ = frame.shape
        landmark_coords = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        
        direction = get_gaze_direction(frame, landmark_coords)
        
        # Draw eye centers
        left_center = np.mean([landmark_coords[idx] for idx in LEFT_EYE], axis=0)
        right_center = np.mean([landmark_coords[idx] for idx in RIGHT_EYE], axis=0)
        cv2.circle(frame, tuple(left_center.astype(int)), 5, (0,255,0), -1)
        cv2.circle(frame, tuple(right_center.astype(int)), 5, (0,255,0), -1)
    
    # Draw UI elements
    draw_direction(frame, direction)
    cv2.line(frame, (w//2, 0), (w//2, h), (255,0,0), 2)
    
    # Show output
    cv2.imshow('Eye Tracking Control', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()