import cv2
import mediapipe as mp
import numpy as np
import pyautogui
import time
import threading
from pynput import mouse
from collections import deque
from sklearn.linear_model import Ridge

# with comments
# Screen size for our model
screen_width, screen_height = pyautogui.size()
print(f"Screen size detected: {screen_width} x {screen_height}")

# Mediapipe setup
mp_face_mesh = mp.solutions.face_mesh
# mesh that goes over face to allow us to detect eyes
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)

# Chosen eye/iris landmark indices
EYE_INDICES = [33, 133, 159, 145, 362, 263, 386, 374]  # outer lids, corners
IRIS_INDICES = list(range(468, 478))  # 10 iris landmarks
HEAD_INDICES = [1, 234, 454]  # nose tip, left cheek, right cheek


# variables
running = True
# tracks raw input from track eyes
eye_data = []
# map of positon points the user clicks
clicked_positions = []
# global variable that is called
latest_eye_position = None
model_x, model_y = None, None
gaze_points = deque(maxlen=5)
last_move_time = time.time()

# this runs seperately in another threzd
# constantly tracks eyes and updates a global variable
def track_eyes_continuously():
    global latest_eye_position
    cap = cv2.VideoCapture(0)
    smoothing = deque(maxlen=5)

    while running:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        if results.multi_face_landmarks:
            lm = results.multi_face_landmarks[0]
            features = []

            # Eye and iris landmarks
            for i in EYE_INDICES + IRIS_INDICES:
                features.extend([lm.landmark[i].x, lm.landmark[i].y])

            # Head orientation (yaw estimate)
            nose = np.array([lm.landmark[1].x, lm.landmark[1].y])
            left_cheek = np.array([lm.landmark[234].x, lm.landmark[234].y])
            right_cheek = np.array([lm.landmark[454].x, lm.landmark[454].y])

            yaw = np.linalg.norm(right_cheek - nose) - np.linalg.norm(nose - left_cheek)
            features.append(yaw)

            smoothing.append(features)
            latest_eye_position = np.mean(smoothing, axis=0)

    cap.release()

# helper to stop too many events from being stored to reduce overhead
def clean_old_events(events):
    current_time = time.time()
    while events and current_time - events[0][0] > 1.0:
        events.popleft()

def gaze_updater():
    while running:
        try:
            pred = predict_gaze()
        except:
            pred = None
        # predicts the gaze based on the msot recent
        if pred:
            gaze_points.append(pred)
            #print(f"Gaze prediction: {pred}")  # <<< Live print to terminal
        time.sleep(0.03)
        # time.sleep(.5)

def predict_gaze():
    # only predicts if that model is trained and has the right attrubutes (BUG FIXED)
    if latest_eye_position is None:
        return None
    if model_x is None or not hasattr(model_x, "coef_") or model_y is None or not hasattr(model_y, "coef_"):
        return None
    eye = np.array(latest_eye_position).reshape(1, -1)
    norm_x = model_x.predict(eye)[0]
    norm_y = model_y.predict(eye)[0]
    x = min(max(0, norm_x * screen_width), screen_width - 1)
    y = min(max(0, norm_y * screen_height), screen_height - 1)
    print(f"Predicted gaze: ({x:.0f}, {y:.0f})")
    return x, y


def makeModel():
    # this makes a regression model and is called again when the
    global model_x, model_y
    if len(eye_data) >= 5:
        # puts in eye data and the positons
        X = np.array(eye_data)
        Y = np.array(clicked_positions)
        model_x = Ridge(alpha=.01)
        model_y = Ridge(alpha=.01)
        model_x.fit(X, Y[:, 0])
        model_y.fit(X, Y[:, 1])

def on_click(x, y, button, pressed):
    # this is for mouse monitoring, it adds new data at every click and retrains
    # print(f"Clicked on {x}, {y}")
    # scaling issue?
    if pressed and latest_eye_position is not None:
        clicked_positions.append((x / screen_width, y / screen_height))
        eye_data.append(latest_eye_position)
        makeModel()

def on_move(x, y):
    # chacks move assuming enough seconds have passed as to not overflow
    global last_move_time
    now = time.time()
    if now - last_move_time > 0.3 and latest_eye_position is not None:
        last_move_time = now
        clicked_positions.append((x / screen_width, y / screen_height))
        eye_data.append(latest_eye_position)
        # retrains
        makeModel()


def on_scroll(x, y, dx, dy):
    pass  # optional for now but could use this fucntion too

def start_listener(move = True):
    # starts mouse monitoring
    # with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
    #     listener.join()
    if move:
        listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    else:
        listener = mouse.Listener(on_move=None, on_click=on_click, on_scroll=on_scroll)
    listener.start()  # starts the listener in the background (non-blocking)
    return listener

# --- Start everything ---

eye_thread = threading.Thread(target=track_eyes_continuously)
eye_thread.start()

predict_thread = threading.Thread(target=gaze_updater)
predict_thread.start()

listener = start_listener()   #Actually start the listener

try:
    # start_listener()

    maze = cv2.imread("maze-image.jpg")
    maze = cv2.resize(maze, (screen_width, screen_height))
    cv2.imshow("Complete the maze with your mouse", maze)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    listener.stop()
    # with open("constTrackOutput.txt", "a") as file:
    #     file.write(f"\n\nUSING JUST THE CLICKS (POST-CALIBRATION)\n\n")
    listener = start_listener(move=False)

    #Creates a run loop to keep the code running
    while running:
        time.sleep(0.03)
except KeyboardInterrupt:
    running = False
    eye_thread.join()
    predict_thread.join()
    listener.stop()   #Stop the listener here when the code breaks
    print("\nAll clicked positions:")
    for pos in clicked_positions:
        print(pos)
    print("\nAll recorded eye positions:")
    for eye in eye_data:
        print(eye)
