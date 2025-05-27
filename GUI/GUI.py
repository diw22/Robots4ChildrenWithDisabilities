# This is a modified GUI-based system for controlling a robot using
# head tracking, eye tracking, and a PS5 controller with Morse code input.
# The UI is designed to be accessible and engaging for children with disabilities.

import tkinter as tk
from tkinter import messagebox
import cv2
import mediapipe as mp
import pygame
import threading
import time

# -------------------- FUN ROBOT INTERFACE --------------------
# Placeholder robot actions (replace with real robot commands)
def send_to_robot(action):
    print(f"[ROBOT] Executing: {action}")

# -------------------- GUI-BASED ACTION EXECUTION --------------------
def perform_action(action):
    send_to_robot(action)
    messagebox.showinfo("Robot Action", f"Robot will now: {action}")

# -------------------- GUI WRAPPER --------------------
def fun_robot_ui():
    root = tk.Tk()
    root.title("Fun Robot Control UI")
    root.geometry("600x400")
    root.configure(bg="#f0f8ff")

    tk.Label(root, text="🎮 Pick a Fun Action for the Robot! 🤖", font=("Comic Sans MS", 18), bg="#f0f8ff").pack(pady=20)

    btn_frame = tk.Frame(root, bg="#f0f8ff")
    btn_frame.pack(pady=10)

    actions = [
        ("🕺 Spin Around", "Spin Around"),
        ("🎵 Play Music", "Play Music"),
        ("🧸 Fetch Toy", "Fetch Toy"),
        ("👋 Wave", "Wave"),
        ("💤 Rest Pose", "Rest Pose"),
        ("👏 Clap", "Clap"),
        ("⬆️ Move Forward", "Move Forward"),
        ("⬇️ Move Backward", "Move Backward"),
        ("⬅️ Turn Left", "Turn Left"),
        ("➡️ Turn Right", "Turn Right")
    ]

    for emoji, label in actions:
        b = tk.Button(btn_frame, text=emoji + " " + label, font=("Comic Sans MS", 14), width=20,
                     command=lambda act=label: perform_action(act))
        b.pack(pady=5)

    tk.Button(root, text="Exit", font=("Comic Sans MS", 12), command=root.destroy).pack(pady=20)
    root.mainloop()

# Example of triggering this after input selection:
if __name__ == '__main__':
    # The user interacts with head/eye/controller GUI first
    # Then they are sent to this fun robot UI to choose action
    fun_robot_ui()