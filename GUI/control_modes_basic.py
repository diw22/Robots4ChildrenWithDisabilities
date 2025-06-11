# control_modes_basic.py

import pygame
import threading
import time

class ControllerManager:
    def __init__(self):
        self.thread = None
        self.running = False
        self.callback = None
        self.joystick = None
        self._init_joystick_once()

    def _init_joystick_once(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() == 0:
            print("[ERROR] No joystick detected.")
            return
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        print(f"[INFO] Controller: {self.joystick.get_name()}")

    def start(self, callback):
        self.stop()  # Ensure previous thread is cleaned up
        self.callback = callback
        self.running = True
        self.thread = threading.Thread(target=self._controller_listener, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None

    def _controller_listener(self):
        if not self.joystick:
            return

        prev_hat = (0, 0)
        prev_button_a = False

        while self.running:
            pygame.event.pump()
            try:
                hat_x, hat_y = self.joystick.get_hat(0)
            except pygame.error as e:
                print(f"[ERROR] Joystick error: {e}")
                break

            if hat_x == -1 and prev_hat != (-1, 0):
                self.callback("Left")
            elif hat_x == 1 and prev_hat != (1, 0):
                self.callback("Right")
            elif hat_y == 1 and prev_hat != (0, 1):
                self.callback("Up")
            elif hat_y == -1 and prev_hat != (0, -1):
                self.callback("Down")

            prev_hat = (hat_x, hat_y)

            button_a = self.joystick.get_button(0)
            if button_a and not prev_button_a:
                self.callback("Centre")
            prev_button_a = button_a

            time.sleep(0.02)

controller_manager = ControllerManager()
