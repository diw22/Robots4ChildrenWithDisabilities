import base64
import json
import os
import sys

import cv2
import numpy as np
import zmq
#import pygame
import time
import mediapipe as mp
#import threading

PYNPUT_AVAILABLE = True

ip = "192.168.137.109"
port = 5555
video_port = 5556

fps = 30

head_direction = "Center"
center_x = None
center_y = None
mp_face_mesh = mp.solutions.face_mesh
head_tracking_enabled = False
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

context = zmq.Context()
socket = context.socket(zmq.PUSH)
connection_string = f"tcp://{ip}:{port}"
socket.connect(connection_string)
socket.setsockopt(zmq.CONFLATE, 1)  

video_socket = context.socket(zmq.PULL)
video_connection_string = f"tcp://{ip}:{video_port}"    
video_socket.connect(video_connection_string)
video_socket.setsockopt(zmq.CONFLATE, 1)

# Define three speed levels and a current index
speed_levels = [
    {"xy": 0.1, "theta": 30},  # slow
    {"xy": 0.2, "theta": 60},  # medium
    {"xy": 0.3, "theta": 90},  # fast
]
speed_index = 0  # Start at slow

# ZeroMQ context and sockets.


cap = cv2.VideoCapture(0)

# Keyboard state for base teleoperation.
running = True

pressed_keys = {
    "forward": False,
    "backward": False,
    "left": False,
    "right": False,
    "rotate_left": False,
    "rotate_right": False,
}

def get_direction(nose_x, nose_y):
    dx = nose_x - center_x
    dy = nose_y - center_y
    threshold = 40
    if abs(dx) < threshold and abs(dy) < threshold:
        return "Center"
    elif abs(dx) > abs(dy):
        return "Right" if dx < 0 else "Left"
    else:
        return "Up" if dy < 0 else "Down"

def start_head_tracking():
    global running, cap, center_x, head_direction, center_y
    if running and cap.isOpened():
        print("headtracking")
        ret, frame = cap.read()
        if ret:
            img_h, img_w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                nose = landmarks[1]
                nose_x = int(nose.x * img_w)
                nose_y = int(nose.y * img_h)
                cv2.circle(frame, (nose_x, nose_y), 5, (0, 255, 0), -1)

                if center_x is not None and center_y is not None:
                    dx = nose_x - center_x
                    dy = nose_y - center_y
                    threshold = 40
                    if abs(dx) < threshold and abs(dy) < threshold:
                        head_direction = "Center"
                    elif abs(dx) > abs(dy):
                        head_direction = "Right" if dx < 0 else "Left"
                    else:
                        head_direction = "Up" if dy < 0 else "Down"
                    cv2.putText(frame, f"Direction: {head_direction}", (10, 70),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                else:
                    cv2.putText(frame, "Press 'c' to calibrate center", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

            # Optional: show video window
            cv2.imshow("Head Tracking", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('c') and results.multi_face_landmarks:
                center_x = int(landmarks[1].x * img_w)
                center_y = int(landmarks[1].y * img_h)
                print(f"[CALIBRATED] Center set to: ({center_x}, {center_y})")

            if head_direction == "Right" :
                pressed_keys["rotate_right"] = True
                pressed_keys["rotate_left"] = False
            elif head_direction == "Left" :
                pressed_keys["rotate_left"] = True 
                pressed_keys["rotate_right"] = False
            elif head_direction == "Down" :
                pressed_keys["forward"] = False
                pressed_keys["backward"] = True   
            elif head_direction == "Up" :
                pressed_keys["backward"] = False
                pressed_keys["forward"] = True
            elif head_direction == "Center" :
                pressed_keys["backward"] = False
                pressed_keys["forward"] = False
                pressed_keys["rotate_right"] = False
                pressed_keys["rotate_left"] = False

            if key == 27:  # ESC
                running = False
    else:            
        cap.release()
        cv2.destroyAllWindows()


def motor_head_control():
    global socket, fps
    while running:
        start_head_tracking()

        start_loop_t = time.perf_counter()
        speed_setting = speed_levels[speed_index]
        xy_speed = speed_setting["xy"]  # e.g. 0.1, 0.25, or 0.4
        theta_speed = speed_setting["theta"]  # e.g. 30, 60, or 90

        # Prepare to assign the position of the leader to the follower
        arm_positions = []
        #for name in leader_arms:
            #pos = leader_arms[name].read("Present_Position")
            #pos_tensor = torch.from_numpy(pos).float()
            #arm_positions.extend(pos_tensor.tolist())


        y_cmd = 0.0  # m/s forward/backward
        x_cmd = 0.0  # m/s lateral
        theta_cmd = 0.0  # deg/s rotation
        if pressed_keys["forward"]:
            y_cmd += xy_speed
        if pressed_keys["backward"]:
            y_cmd -= xy_speed
        if pressed_keys["left"]:
            x_cmd += xy_speed
        if pressed_keys["right"]:
            x_cmd -= xy_speed
        if pressed_keys["rotate_left"]:
            theta_cmd += theta_speed
        if pressed_keys["rotate_right"]:
            theta_cmd -= theta_speed

        wheel_commands = body_to_wheel_raw(x_cmd, y_cmd, theta_cmd)

        message = {"raw_velocity": wheel_commands}
        print(f"[DEBUG] Sending ZMQ message: {message}")
        socket.send_string(json.dumps(message))
        
        dt_s = time.perf_counter() - start_loop_t
        seconds = 1 / fps - dt_s
        end_time = time.perf_counter() + seconds
        while time.perf_counter() < end_time:
            pass


def degps_to_raw(degps: float) -> int:
    steps_per_deg = 4096.0 / 360.0
    speed_in_steps = abs(degps) * steps_per_deg
    speed_int = int(round(speed_in_steps))
    if speed_int > 0x7FFF:
        speed_int = 0x7FFF
    if degps < 0:
        return speed_int | 0x8000
    else:
        return speed_int & 0x7FFF

def body_to_wheel_raw(
    x_cmd: float,
    y_cmd: float,
    theta_cmd: float,
    wheel_radius: float = 0.05,
    base_radius: float = 0.125,
    max_raw: int = 3000,
) -> dict:
    """
    Convert desired body-frame velocities into wheel raw commands.

    Parameters:
        x_cmd      : Linear velocity in x (m/s).
        y_cmd      : Linear velocity in y (m/s).
        theta_cmd  : Rotational velocity (deg/s).
        wheel_radius: Radius of each wheel (meters).
        base_radius : Distance from the center of rotation to each wheel (meters).
        max_raw    : Maximum allowed raw command (ticks) per wheel.

    Returns:
        A dictionary with wheel raw commands:
            {"left_wheel": value, "back_wheel": value, "right_wheel": value}.

    Notes:
        - Internally, the method converts theta_cmd to rad/s for the kinematics.
        - The raw command is computed from the wheels angular speed in deg/s
        using degps_to_raw(). If any command exceeds max_raw, all commands
        are scaled down proportionally.
    """
    # Convert rotational velocity from deg/s to rad/s.
    theta_rad = theta_cmd * (np.pi / 180.0)
    # Create the body velocity vector [x, y, theta_rad].
    velocity_vector = np.array([x_cmd, y_cmd, theta_rad])

    # Define the wheel mounting angles (defined from y axis cw)
    angles = np.radians(np.array([300, 180, 60]))
    # Build the kinematic matrix: each row maps body velocities to a wheel’s linear speed.
    # The third column (base_radius) accounts for the effect of rotation.
    m = np.array([[np.cos(a), np.sin(a), base_radius] for a in angles])

    # Compute each wheel’s linear speed (m/s) and then its angular speed (rad/s).
    wheel_linear_speeds = m.dot(velocity_vector)
    wheel_angular_speeds = wheel_linear_speeds / wheel_radius

    # Convert wheel angular speeds from rad/s to deg/s.
    wheel_degps = wheel_angular_speeds * (180.0 / np.pi)

    # Scaling
    steps_per_deg = 4096.0 / 360.0
    raw_floats = [abs(degps) * steps_per_deg for degps in wheel_degps]
    max_raw_computed = max(raw_floats)
    if max_raw_computed > max_raw:
        scale = max_raw / max_raw_computed
        wheel_degps = wheel_degps * scale

    # Convert each wheel’s angular speed (deg/s) to a raw integer.
    wheel_raw = [degps_to_raw(deg) for deg in wheel_degps]

    return {"left_wheel": wheel_raw[0], "back_wheel": wheel_raw[1], "right_wheel": wheel_raw[2]}







motor_head_control()

socket.close()
video_socket.close()
    # Mobile Manipulator: Head-Tracking Teleoperation only
# Replaces prior code with a simplified head-based base control.
