import cv2
import pygame
import time
import requests
import platform
import json

BASE_URL = "http://0.0.0.0:80"

device = platform.system()

teleoperation = False


STEP_SIZE = 1 # cm

# Define relative movement and rotation vectors
up = { "x": 0, "y": 0, "z": 0, "rz": 0, "rx": STEP_SIZE * 3.14, "ry": 0 }
down = { "x": 0, "y": 0, "z": 0, "rz": 0, "rx": -STEP_SIZE * 3.14, "ry": 0 }
right = { "x": 0, "y": 0, "z": 0, "rz": -STEP_SIZE * 3.14, "rx": 0, "ry": 0 }
left = { "x": 0, "y": 0, "z": 0, "rz": STEP_SIZE * 3.14, "rx": 0, "ry": 0 }


f = { "x": 0, "y": 0, "z": STEP_SIZE, "rz": 0, "rx": 0, "ry": 0 }
v = { "x": 0, "y": 0, "z": -STEP_SIZE, "rz": 0, "rx": 0, "ry": 0 }
ArrowUp = { "x": STEP_SIZE, "y": 0, "z": 0, "rz": 0, "rx": 0, "ry": 0 }
ArrowDown = { "x": -STEP_SIZE, "y": 0, "z": 0, "rz": 0, "rx": 0, "ry": 0 }
ArrowRight = { "x": 0, "y": 0, "z": 0, "rz": -STEP_SIZE * 3.14, "rx": 0, "ry": 0 }
ArrowLeft = { "x": 0, "y": 0, "z": 0, "rz": STEP_SIZE * 3.14, "rx": 0, "ry": 0 }
d = { "x": 0, "y": 0, "z": 0, "rz": 0, "rx": STEP_SIZE * 3.14, "ry": 0 }
g = { "x": 0, "y": 0, "z": 0, "rz": 0, "rx": -STEP_SIZE * 3.14, "ry": 0 }
b = { "x": 0, "y": 0, "z": 0, "rz": 0, "rx": 0, "ry": STEP_SIZE * 3.14 }
c = { "x": 0, "y": 0, "z": 0, "rz": 0, "rx": 0, "ry": -STEP_SIZE * 3.14 }
open = {
    "x": None,
    "y": None,
    "z": None,
    "rx": None,
    "ry": None,
    "rz": None,
    "open": 1
}
close = {
    "x": None,
    "y": None,
    "z": None,
    "rx": None,
    "ry": None,
    "rz": None,
    "open": 0
}

# Map semantic command names to vector payloads
commands = {
    'translate_z_forward':         f,
    'translate_z_backward':        v,
    'translate_x_up':        ArrowUp,
    'translate_x_down':      ArrowDown,
    'yaw_left':           ArrowLeft,
    'yaw_right':          ArrowRight,
    'roll_left':          c,
    'roll_right':         b,
    'pitch_up':           d,
    'pitch_down':         g,
    'toggle_open':   open,
    'toggle_close':    close,
}


morse_input_delay = 0.5  # seconds
last_morse_time = 0


def handle_morse(direction):
    global morse_buffer, last_morse_time
    current_time = time.time()

    if direction in ["Left", "Right"]:
        if current_time - last_morse_time < morse_input_delay:
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

pygame.init()
pygame.joystick.init()

ds5 = pygame.joystick.Joystick(0)
ds5.init()

print(f"[INFO] Controller: {ds5.get_name()}")

running = True
morse_mode = False

# Main loop: poll joystick, map buttons to commands, send to robot if enabled
while running:
    pygame.event.pump()

    data = None
    if device == "Windows" or device == "Darwin":

        if ds5.get_button(0):
            # Button 0 held: pitch/roll control
            if ds5.get_button(11):
                data = commands["pitch_up"]
            if ds5.get_button(12):
                data = commands["pitch_down"]
            if ds5.get_button(13):
                data = commands["roll_left"]
            if ds5.get_button(14):
                data = commands["roll_right"]
            

        elif ds5.get_button(1):
            # Button 1 held: z-translation or gripper toggle
            if ds5.get_button(11):
                data = commands["translate_z_forward"]
            if ds5.get_button(12):
                data = commands["translate_z_backward"]
            if ds5.get_button(13):
                data = commands["toggle_open"]
            if ds5.get_button(14):
                data = commands["toggle_close"]
            

        else:
            # No face button: x-translation or yaw control
            if ds5.get_button(11):
                data = commands["translate_x_up"]
            if ds5.get_button(12):
                data = commands["translate_x_down"]
            if ds5.get_button(13):
                data = commands["yaw_left"]
            if ds5.get_button(14):
                data = commands["yaw_right"]

    else:
        # On non-Windows/Mac, use D-pad (hat) for basic 4-way control
        button_map = {
                (0,1): up,
                (0,-1): down,
                (-1,0): left,
                (1,0): right
            }
        
        for index, name in button_map.items():
            if button_map[index] == ds5.get_hat(0):
                data = name

    # Build request params for the robot    
    params = {
        "robot_id": 0
    }

    # If a command is selected and teleoperation is on, send it
    if data is not None and teleoperation:
        response = requests.post(f"{BASE_URL}/move/relative", json=data, params=params)
        print(response.status_code, response.text)
        print(data)
        


    mode_text = "Morse Mode" if morse_mode else "Joystick Mode"

    '''key = cv2.waitKey(1) & 0xFF
    if key == 27:
        print("[INFO] Exiting...")
        break'''

    # Toggle teleoperation on pressing buttons 0 + 1 together
    if ds5.get_button(0):
        if ds5.get_button(1):
            teleoperation = not teleoperation
            print(f"[INFO] Teleoperation {'enabled' if teleoperation else 'disabled'}")
            time.sleep(1)