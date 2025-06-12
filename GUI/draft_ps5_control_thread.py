import cv2
import pygame
import time
import requests
import platform
import json
import threading

BASE_URL = "http://raspberrypi.local"
STEP_SIZE = 1  # cm
device = platform.system()

teleoperation = False
morse_input_delay = 0.5
last_morse_time = 0
morse_buffer = ""

# Movement vectors
up = {"x": 0, "y": 0, "z": 0, "rz": 0, "rx": STEP_SIZE * 3.14, "ry": 0}
down = {"x": 0, "y": 0, "z": 0, "rz": 0, "rx": -STEP_SIZE * 3.14, "ry": 0}
right = {"x": 0, "y": 0, "z": 0, "rz": -STEP_SIZE * 3.14, "rx": 0, "ry": 0}
left = {"x": 0, "y": 0, "z": 0, "rz": STEP_SIZE * 3.14, "rx": 0, "ry": 0}

f = {"x": 0, "y": 0, "z": STEP_SIZE, "rz": 0, "rx": 0, "ry": 0}
v = {"x": 0, "y": 0, "z": -STEP_SIZE, "rz": 0, "rx": 0, "ry": 0}
ArrowUp = {"x": STEP_SIZE, "y": 0, "z": 0, "rz": 0, "rx": 0, "ry": 0}
ArrowDown = {"x": -STEP_SIZE, "y": 0, "z": 0, "rz": 0, "rx": 0, "ry": 0}
ArrowRight = {"x": 0, "y": 0, "z": 0, "rz": -STEP_SIZE * 3.14, "rx": 0, "ry": 0}
ArrowLeft = {"x": 0, "y": 0, "z": 0, "rz": STEP_SIZE * 3.14, "rx": 0, "ry": 0}
d = {"x": 0, "y": 0, "z": 0, "rz": 0, "rx": STEP_SIZE * 3.14, "ry": 0}
g = {"x": 0, "y": 0, "z": 0, "rz": 0, "rx": -STEP_SIZE * 3.14, "ry": 0}
b = {"x": 0, "y": 0, "z": 0, "rz": 0, "rx": 0, "ry": STEP_SIZE * 3.14}
c = {"x": 0, "y": 0, "z": 0, "rz": 0, "rx": 0, "ry": -STEP_SIZE * 3.14}

open = {"x": None, "y": None, "z": None, "rx": None, "ry": None, "rz": None, "open": 1}
close = {"x": None, "y": None, "z": None, "rx": None, "ry": None, "rz": None, "open": 0}

commands = {
    'translate_z_forward': f,
    'translate_z_backward': v,
    'translate_x_up': ArrowUp,
    'translate_x_down': ArrowDown,
    'yaw_left': ArrowLeft,
    'yaw_right': ArrowRight,
    'roll_left': c,
    'roll_right': b,
    'pitch_up': d,
    'pitch_down': g,
    'toggle_open': open,
    'toggle_close': close,
}

# Thread management
control_thread = None
stop_event = threading.Event()


def handle_morse(direction):
    global morse_buffer, last_morse_time
    current_time = time.time()

    if direction in ["Left", "Right"] and current_time - last_morse_time < morse_input_delay:
        print(f"[SKIP] Ignored {direction} due to delay")
        return

    last_morse_time = current_time
    if direction == "Left":
        morse_buffer += "."
    elif direction == "Right":
        morse_buffer += "-"
    elif direction == "Up":
        print(f"[MORSE SUBMIT] {morse_buffer}")
        morse_buffer = ""
    elif direction == "Down":
        morse_buffer = morse_buffer[:-1]

    print(f"[MORSE BUFFER] {morse_buffer}")


def run_ps5_control():
    global teleoperation
    pygame.init()
    pygame.joystick.init()
    print("[INFO] Initializing PS5 controller...")
    

    try:
        ds5 = pygame.joystick.Joystick(0)
        ds5.init()
        print(f"[INFO] Controller: {ds5.get_name()}")
    except Exception as e:
        print(f"[ERROR] Could not initialize PS5 controller: {e}")
        return

    morse_mode = False

    while not stop_event.is_set():
        pygame.event.pump()
        data = None
        #print("beans 2...")

        if device == "Darwin":
            if ds5.get_button(0):
                if ds5.get_button(11):
                    data = commands["pitch_up"]
                if ds5.get_button(12):
                    data = commands["pitch_down"]
                if ds5.get_button(13):
                    data = commands["roll_left"]
                if ds5.get_button(14):
                    data = commands["roll_right"]
            elif ds5.get_button(1):
                if ds5.get_button(11):
                    data = commands["translate_z_forward"]
                if ds5.get_button(12):
                    data = commands["translate_z_backward"]
                if ds5.get_button(13):
                    data = commands["toggle_open"]
                if ds5.get_button(14):
                    data = commands["toggle_close"]
            else:
                if ds5.get_button(11):
                    data = commands["translate_x_up"]
                if ds5.get_button(12):
                    data = commands["translate_x_down"]
                if ds5.get_button(13):
                    data = commands["yaw_left"]
                if ds5.get_button(14):
                    data = commands["yaw_right"]
        else:
            # Use Xbox-style D-pad from get_hat(0)
            hat = ds5.get_hat(0)
            hat_x, hat_y = ds5.get_hat(0)
            if hat != (0, 0):
                print(f"[DEBUG] Hat state: {hat_x, hat_y}")
            if hat_y == 1:
                data = f  # forward
            elif hat_y == -1:
                data = v  # backward
            elif hat_x == -1:
                data = commands["yaw_left"]
            elif hat_x == 1:
                data = commands["yaw_right"]

            if data is not None and teleoperation:
                try:
                    response = requests.post(f"{BASE_URL}/move/relative", json=data, params={"robot_id": 0})
                    print(response.status_code, response.text)
                    #print(f"({data}) sent to robot")
                except Exception as e:
                    print(f"[ERROR] Failed to send request: {e}")

            if ds5.get_button(0) and ds5.get_button(1):
                teleoperation = not teleoperation
                print(f"[INFO] Teleoperation {'enabled' if teleoperation else 'disabled'}")
                time.sleep(1)



def start_ps5_control():
    global control_thread, stop_event
    if control_thread is None or not control_thread.is_alive():
        print("[INFO] Starting PS5 control thread...")
        stop_event.clear()
        control_thread = threading.Thread(target=run_ps5_control, daemon=True)
        control_thread.start()


def stop_ps5_control():
    print("[INFO] Stopping PS5 control thread...")
    stop_event.set()
