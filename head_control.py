import cv2
import mediapipe as mp
import requests
import numpy as np

# Head-controlled teleoperation with refined pitch detection via angle
BASE_URL = "http://0.0.0.0:80"

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Teleoperation flag and movement scale
teleoperation = False
STEP_SIZE = 1  # cm per command

# Movement commands
commands = {
    'translate_z_forward':   {'x':-STEP_SIZE,'y':0,'z':0,'rz':0,'rx':0,'ry':0},
    'translate_z_backward':  {'x':STEP_SIZE,'y':0,'z':0,'rz':0,'rx':0,'ry':0},
    'translate_x_up':        {'x':0,'y':0,'z': STEP_SIZE,'rz':0,'rx':0,'ry':0},
    'translate_x_down':      {'x':0,'y':0,'z':-STEP_SIZE,'rz':0,'rx':0,'ry':0},
    'yaw_left':              {'x':0,'y':0,'z':0,'rz': STEP_SIZE*3.14,'rx':0,'ry':0},
    'yaw_right':             {'x':0,'y':0,'z':0,'rz':-STEP_SIZE*3.14,'rx':0,'ry':0},
    'roll_left':             {'x':0,'y':0,'z':0,'rz':0,'rx':0,'ry':STEP_SIZE*3.14},
    'roll_right':            {'x':0,'y':0,'z':0,'rz':0,'rx':0,'ry':-STEP_SIZE*3.14},
    'pitch_up':              {'x':0,'y':0,'z':0,'rz':0,'rx': STEP_SIZE*3.14,'ry':0},
    'pitch_down':            {'x':0,'y':0,'z':0,'rz':0,'rx':-STEP_SIZE*3.14,'ry':0},
}

# Calibration baselines for nose, roll, and pitch angle
baseline = {
    'nose_z': None,
    'nose_x': None,
    'nose_y': None,
    'eye_slope': None,
    'pitch_angle': None
}

# Detection thresholds
dth = {
    'z': 0.008,
    'x': 0.04,
    'y': 0.06,
    'roll': 0.25,
    'pitch': 0.1
}

# Helper: get normalized XY
def get_xy(lm, idx):
    return np.array([lm[idx].x, lm[idx].y])

# Main loop
cap = cv2.VideoCapture(0)
print("[INFO] Press C to calibrate, T to toggle teleop, ESC to quit.")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = face_mesh.process(rgb)

    if res.multi_face_landmarks:
        lm = res.multi_face_landmarks[0].landmark
        # key landmarks
        nose = np.array([lm[1].x, lm[1].y, lm[1].z])
        chin = np.array([lm[152].x, lm[152].y, lm[152].z])
        left_eye = get_xy(lm, 133)
        right_eye = get_xy(lm, 362)

        if baseline['nose_z'] is None:
            cv2.putText(frame, 'Press C to calibrate', (10,40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
            action, probs = 'center', {'center': 1.0}
        else:
            # compute deltas
            dz = nose[2] - baseline['nose_z']
            dx = nose[0] - baseline['nose_x']
            dy = baseline['nose_y'] - nose[1]
            slope = ((right_eye[1] - left_eye[1]) / (right_eye[0] - left_eye[0] + 1e-6)) - baseline['eye_slope']
            # compute current pitch angle (chin-to-nose): radians
            pitch_angle = np.arctan2(chin[1] - nose[1], chin[2] - nose[2])
            dp = pitch_angle - baseline['pitch_angle']

            # debug print
            dbg = f"dz:{dz:.3f} dx:{dx:.3f} dy:{dy:.3f} sl:{slope:.3f} dp:{dp:.3f}"
            cv2.putText(frame, dbg, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)

            # scoring
            scores = {
                'center': 0.1,
                'translate_z_forward':   max(dz - dth['z'], 0) + 0.1,
                'translate_z_backward':  max(-dz - dth['z'], 0) + 0.1,
                'translate_x_up':        max(dy - dth['y'], 0),
                'translate_x_down':      max(-dy - dth['y'], 0),
                'yaw_left':              max(-dx - dth['x'], 0) + 0.1,
                'yaw_right':             max(dx - dth['x'], 0) + 0.1,
                'roll_left':             max(-slope - dth['roll'], 0),
                'roll_right':            max(slope - dth['roll'], 0),
                'pitch_up':              max(dp - dth['pitch'], 0) + 0.1,
                'pitch_down':            max(-dp - dth['pitch'], 0) + 0.1,
            }
            total = sum(scores.values()) + 1e-6
            probs = {k: v/total for k, v in scores.items()}
            action = max(probs, key=probs.get)
            if teleoperation and action != 'center':
                requests.post(f"{BASE_URL}/move/relative", json=commands[action], params={"robot_id":0})

        # draw probabilities
        y0, dy = 80, 24
        for i, (act, p) in enumerate(probs.items()):
            color = (0,255,0) if act == action else (255,255,255)
            cv2.putText(frame, f"{act}: {p:.2f}", (10, y0 + i*dy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(frame, f"Action: {action}", (10, y0 + len(probs)*dy), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,255,0), 2)

    cv2.putText(frame, f"Teleop: {'ON' if teleoperation else 'OFF'}", (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    cv2.imshow('Head Teleop 3D', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break
    elif key == ord('t'):
        teleoperation = not teleoperation
    elif key == ord('c') and res.multi_face_landmarks:
        baseline['nose_z'] = lm[1].z
        baseline['nose_x'] = lm[1].x
        baseline['nose_y'] = lm[1].y
        baseline['eye_slope'] = (right_eye[1] - left_eye[1]) / (right_eye[0] - left_eye[0] + 1e-6)
        # baseline pitch angle
        chin_z = lm[152].z
        baseline['pitch_angle'] = np.arctan2(lm[152].y - lm[1].y, chin_z - lm[1].z)
        print(f"[CAL] nz={baseline['nose_z']:.3f}, nx={baseline['nose_x']:.3f}, ny={baseline['nose_y']:.3f}, slope={baseline['eye_slope']:.2f}, pitch_ang={baseline['pitch_angle']:.3f}")

cap.release()
cv2.destroyAllWindows()
