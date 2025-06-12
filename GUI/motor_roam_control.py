#motor_roam_control.py

import base64
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
#import torch
import threading
import zmq
from xbox_input import XboxController
import pygame
import time

ip = "192.168.137.109"
port = 5555
video_port = 5556

fps = 30

#xbx = XboxController()

pressed_keys = {
    "forward": False,
    "backward": False,
    "left": False,
    "right": False,
    "rotate_left": False,
    "rotate_right": False,
}



speed_levels = [
        {"xy": 0.1, "theta": 30}, # Low speed
        {"xy": 0.2, "theta": 60}, # Medium speed
        {"xy": 0.3, "theta": 90}  # High speed
]

speed_index = 0

control_thread = None
stop_event = threading.Event()
PYNPUT_AVAILABLE = True
try:
    # Only import if there's a valid X server or if we're not on a Pi
    if ("DISPLAY" not in os.environ) and ("linux" in sys.platform):
        print("No DISPLAY set. Skipping pynput import.")
        raise ImportError("pynput blocked intentionally due to no display.")

    from pynput import keyboard
except ImportError:
    keyboard = None
    PYNPUT_AVAILABLE = False
except Exception as e:
    keyboard = None
    PYNPUT_AVAILABLE = False
    print(f"Could not import pynput: {e}")
    
def start_motor_roam_control():
    global control_thread, stop_event, speed_index
    
    context = zmq.Context()
    socket = context.socket(zmq.PUSH)
    connection_string = f"tcp://{ip}:{port}"
    socket.connect(connection_string)
    socket.setsockopt(zmq.CONFLATE, 1)  

    video_socket = context.socket(zmq.PULL)
    video_connection_string = f"tcp://{ip}:{video_port}"    
    video_socket.connect(video_connection_string)
    video_socket.setsockopt(zmq.CONFLATE, 1)
    
    xbx = XboxController()
    
    if not xbx.CONTROLLER_AVAILABLE:
        print("[ERROR] Xbox controller not available. Exiting control thread.")
        return  
    
    
    speed_index = 0
    if control_thread is None or not control_thread.is_alive():
        print("[INFO] Starting PS5 control thread...")
        stop_event.clear()
        control_thread = threading.Thread(target=motor_ps5_control(xbx,socket), daemon=True)
        control_thread.start()
        
def stop_motor_roam_control():
    print("[INFO] Stopping PS5 control thread...")
    stop_event.set()
    if control_thread is not None:
        control_thread.join()
        control_thread = None
    print("[INFO] PS5 control thread stopped.")

def motor_ps5_control(xbx,socket):
    while not stop_event.is_set():
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
        pygame.event.pump()
        xbox_keys(xbx)

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
        #print(f"[DEBUG] Sending ZMQ message: {message}")
        socket.send_string(json.dumps(message))
        
        dt_s = time.perf_counter() - start_loop_t
        seconds = 1 / fps - dt_s
        end_time = time.perf_counter() + seconds
        while time.perf_counter() < end_time:
            pass
    
def xbox_keys(xbx):
    #hat_x, hat_y = xbx.controller.get_hat(0)
    hat_x, hat_y = xbx.controller.get_hat(0)
    global speed_index

    if xbx.controller.get_button(1):
        if hat_y == 1:
            speed_index = min(speed_index + 1, 2)
            print(f"Speed index increased to {speed_index}")
            time.sleep(1)
        elif hat_y == -1:
            speed_index = max(speed_index - 1, 0)
            print(f"Speed index decreased to {speed_index}")
            time.sleep(1)
    else:
        if hat_y == 1:
            pressed_keys["forward"] = True
            pressed_keys["backward"] = False
        elif hat_y == -1:
            pressed_keys["backward"] = True 
            pressed_keys["forward"] = False
        else:
            pressed_keys["backward"] = False 
            pressed_keys["forward"] = False

    if xbx.controller.get_button(0):
        pressed_keys["left"] = False 
        pressed_keys["right"] = False
        if hat_x == 1:
            pressed_keys["rotate_right"] = True
            pressed_keys["rotate_left"] = False 
        elif hat_x == -1:
            pressed_keys["rotate_left"] = True 
            pressed_keys["rotate_right"] = False
        else:
            pressed_keys["rotate_left"] = False 
            pressed_keys["rotate_right"] = False    
    else:
        pressed_keys["rotate_left"] = False 
        pressed_keys["rotate_right"] = False          
        if hat_x == 1:
            pressed_keys["right"] = True
            pressed_keys["left"] = False
        elif hat_x == -1:
            pressed_keys["left"] = True 
            pressed_keys["right"] = False
        else:
            pressed_keys["left"] = False 
            pressed_keys["right"] = False

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