import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


import random

import cv2
import subprocess
import mediapipe as mp

from sklearn.linear_model import LinearRegression
from pynput import mouse
from collections import deque
import time
from new_focus import *
from screenshot_scoring import parseImage
from PIL import ImageGrab

from gaze_tracking import GazeTracker
from Q_Learning import QLearner
from ui import initialize_interface

# FUNCTION FOR COMMANDS
def get_command_and_target(action, important_word_coords, focus, isFocused, screenWidth, screenHeight, timeOffscreen, onCanvas):
    if not important_word_coords:
        return action, (0, 0)
    if not onCanvas:
        isFocused = False
        # action = 6
        target = (random.randint(200, screenWidth//2), 74)
    elif timeOffscreen > 10:
        isFocused = False
        action = 8
        target = (screenWidth//2, screenHeight//2)
    elif focus > 90:
        if not isFocused:
            isFocused = True
            action = 7
            target = (screenWidth-200, screenHeight-151)
        else:
            isFocused = True
            action = 0
            target = (screenWidth-200, screenHeight-151)
    else:
        isFocused = False
        target = important_word_coords
    return action, target, isFocused



def main():
    print("Starting main")
    try:
        username = initialize_interface()
    except:
        print("You closed the application too early! Please try again.")
        return
    user_csv = f"User_Data/{username.lower()}_data.csv"
    q_learning_csv = f"User_Data/{username.lower()}_q_table.npy"
    if not os.path.exists(user_csv):
        with open(user_csv, 'w') as user_write:
            user_write.write("Improved, Change in Score, Final Score, Command\n")
    listener = GazeTracker()
    listener.start(move=True)  # Enable mouse movement for calibration
    learner = QLearner(q_learning_csv)

    # === Calibration Step ===
    try:
        # Show maze image and wait for calibration clicks
        maze = cv2.imread("maze-image-2.jpeg")
        screen_width, screen_height = listener.width, listener.height
        maze = cv2.resize(maze, (screen_width, screen_height))
        cv2.imshow("Complete the maze with your mouse", maze)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        # Stop movement tracking after calibration
        listener.listener.stop()
        screenmate_process = subprocess.Popen(["./wizard.exe"])
         # Only clicks now
    except Exception as e:
        listener.listener.stop()
        print(f"Calibration failed or skipped: {e}")

    try:
        listener.start_listener(move=False)
        # === Begin Focus + Q-Learning Loop ===
        isFocused = False
        while True:
            screenshot = ImageGrab.grab()
            screen_width, screen_height = screenshot.size
            screenshot.save("screenshot.png")
            parseImage("screenshot.png")
            # print(f"screenshot with dimensions {screen_width}x{screen_height}")

            screen_x, screen_y = listener.get_latest_gaze() or (0, 0)

            foc_score, important_word_coords, timeOff, canvas = focus_score((screen_x, screen_y), "FINAL_ACTUAL.csv", screenshot, username)
            state = learner.get_state(foc_score)
            action = learner.choose_action(state)
            command, coords, isFocused = get_command_and_target(action, important_word_coords, foc_score, isFocused, screen_width, screen_height, timeOff, canvas)

            with open("action_coords.csv", 'w') as action_file:
                # if command == 0 and foc_score > 90:
                #     action_file.write(f'{screen_width - 200}, {150}, {command}, {screen_width}, {screen_height}')
                # else:
                action_file.write(f'{coords[0]}, {screen_height - coords[1] - 1}, {command}, {screen_width}, {screen_height}')

            time.sleep(5)

            new_x, new_y = listener.get_latest_gaze() or (0, 0)
            new_score, _, _, _ = focus_score((new_x, new_y), "FINAL_ACTUAL.csv", screenshot, username)
            reward = new_score - foc_score
            new_state = learner.get_state(new_score)
            learner.update(state, action, reward, new_state)
            learner.save_q_table()
            with open(user_csv, "a") as user_write:
                user_write.write(f'{reward > 0}, {reward}, {new_score}, {command}\n')

            time.sleep(0.5)

    except KeyboardInterrupt:
        listener.stop()


    except Exception as e:
        listener.stop()
        print(e)


if __name__ == "__main__":
    main()
