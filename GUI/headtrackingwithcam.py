import cv2
import mediapipe as mp
import threading
import time

class HeadTracker:
    def __init__(self, direction_callback=None, threshold=40, queue = None):
        self.threshold = threshold
        self.callback = direction_callback
        self.running = False
        #self.cap = cv2.VideoCapture(0)
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
        self.calibrated_x = None
        self.calibrated_y = None
        self.NOSE_ID = 1
        self.qRgb = queue

    def start(self):
        self.running = True
        threading.Thread(target=self._track_loop, daemon=True).start()

    def stop(self):
        self.running = False
        #self.cap.release()

    def _track_loop(self):
        last_direction = None
        last_sent = time.time()

        while self.running:
            #ret, frame = self.cap.read()
            #if not ret:
            #    continue

            inRgb = self.qRgb.get()

            frame = inRgb.getCvFrame()

            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if results.multi_face_landmarks:
                nose = results.multi_face_landmarks[0].landmark[self.NOSE_ID]
                x = int(nose.x * w)
                y = int(nose.y * h)

                if self.calibrated_x is None:
                    self.calibrated_x, self.calibrated_y = x, y
                    print(f"[HEADTRACKING] Calibrated at ({x}, {y})")
                    continue

                dx = x - self.calibrated_x
                dy = y - self.calibrated_y

                if abs(dx) < self.threshold and abs(dy) < self.threshold:
                    direction = "Centre"
                elif abs(dx) > abs(dy):
                    direction = "Left" if dx < 0 else "Right"
                else:
                    direction = "Up" if dy < 0 else "Down"

                if direction != last_direction and time.time() - last_sent > 0.3:
                    if self.callback:
                        self.callback(direction)
                    last_direction = direction
                    last_sent = time.time()
