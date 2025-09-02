import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import threading
from pynput import mouse
from collections import deque
from sklearn.linear_model import Ridge


class GazeTracker:
    def __init__(self):
        self.width, self.height = pyautogui.size()
        print(f"Screen size detected: {self.width} x {self.height}")
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=False, max_num_faces=1, refine_landmarks=True)

        self.EYE_INDICES = [33, 133, 159, 145, 362, 263, 386, 374]
        self.IRIS_INDICES = list(range(468, 478))
        self.HEAD_INDICES = [1, 234, 454]

        self.running = False
        self.eye_data = []
        self.clicked_positions = []
        self.latest_eye_position = None
        self.model_x, self.model_y = None, None
        self.gaze_points = deque(maxlen=5)
        self.last_move_time = time.time()
        self.listener = None

        self.eye_thread = threading.Thread(target=self.track_eyes_continuously)
        self.predict_thread = threading.Thread(target=self.gaze_updater)

    def start(self, move=True):
        if not self.running:
            self.running = True
            self.eye_thread.start()
            self.predict_thread.start()
        self.start_listener(move)

    def start_listener(self, move=True):
        # If a listener already exists and is running, stop it safely
        if self.listener and self.listener.running:
            print("Stopping existing mouse listener...")
            self.listener.stop()
            self.listener.join()

        print("Starting mouse listener...")
        if move:
            self.listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click)
        else:
            self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

    def stop(self):
        self.running = False
        if self.eye_thread.is_alive():
            self.eye_thread.join()
        if self.predict_thread.is_alive():
            self.predict_thread.join()
        if self.listener:
            self.listener.stop()
            self.listener.join()

    def track_eyes_continuously(self):
        cap = cv2.VideoCapture(0)
        smoothing = deque(maxlen=5)
        while self.running:
            ret, frame = cap.read()
            if not ret:
                continue
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb)

            if results.multi_face_landmarks:
                lm = results.multi_face_landmarks[0]
                features = []

                for i in self.EYE_INDICES + self.IRIS_INDICES:
                    features.extend([lm.landmark[i].x, lm.landmark[i].y])

                nose = np.array([lm.landmark[1].x, lm.landmark[1].y])
                left_cheek = np.array([lm.landmark[234].x, lm.landmark[234].y])
                right_cheek = np.array([lm.landmark[454].x, lm.landmark[454].y])
                yaw = np.linalg.norm(right_cheek - nose) - np.linalg.norm(nose - left_cheek)
                features.append(yaw)

                smoothing.append(features)
                self.latest_eye_position = np.mean(smoothing, axis=0)

        cap.release()

    def gaze_updater(self):
        while self.running:
            try:
                pred = self.predict_gaze()
                if pred:
                    self.gaze_points.append(pred)
            except Exception as e:
                print(f"Gaze prediction failed: {e}")
            time.sleep(0.03)

    def predict_gaze(self):
        if self.latest_eye_position is None or not self.model_x or not self.model_y:
            return None
        eye = np.array(self.latest_eye_position).reshape(1, -1)
        norm_x = self.model_x.predict(eye)[0]
        norm_y = self.model_y.predict(eye)[0]
        x = min(max(0, norm_x * self.width), self.width - 1)
        y = min(max(0, norm_y * self.height), self.height - 1)
        print(f"Predicted gaze: ({x:.0f}, {y:.0f})")
        return x, y

    def make_model(self):
        if len(self.eye_data) >= 5:
            X = np.array(self.eye_data)
            Y = np.array(self.clicked_positions)
            self.model_x = Ridge(alpha=0.01)
            self.model_y = Ridge(alpha=0.01)
            self.model_x.fit(X, Y[:, 0])
            self.model_y.fit(X, Y[:, 1])

    def on_click(self, x, y, button, pressed):
        if pressed and self.latest_eye_position is not None:
            print("Clicked at", x, y)
            self.clicked_positions.append((x / self.width, y / self.height))
            self.eye_data.append(self.latest_eye_position)
            self.make_model()

    def on_move(self, x, y):
        now = time.time()
        if now - self.last_move_time > 0.3 and self.latest_eye_position is not None:
            self.last_move_time = now
            self.clicked_positions.append((x / self.width, y / self.height))
            self.eye_data.append(self.latest_eye_position)
            self.make_model()

    def get_latest_gaze(self):
        if self.gaze_points:
            return self.gaze_points[-1]
        return None
