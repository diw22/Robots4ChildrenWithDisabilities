# control_modes_basic.py

import pygame
import threading
import time

class ControllerManager:
    def __init__(self):
        self.thread = None
        self.running = False
        self.callback = None

    def start(self, callback):
        self.callback = callback
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._controller_listener, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join()
            self.thread = None

    def _controller_listener(self):
        pygame.init()
        pygame.joystick.init()
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        print(f"[INFO] Controller: {joystick.get_name()}")

        prev_state = {'Up': False, 'Down': False, 'Left': False, 'Right': False, 'Centre': False}
        button_map = {
            'Centre': 1,  # Cross button
            'Up': 11,
            'Down': 12,
            'Left': 13,
            'Right': 14
        }
        cooldown = {name: 0 for name in button_map}
        while self.running:
            pygame.event.pump()
            for name, index in button_map.items():
                is_pressed = joystick.get_button(index)
                now = time.time()
                if is_pressed and not prev_state[name] and now - cooldown[name] > 0.2:
                    cooldown[name] = now
                    if self.callback:
                            self.callback(name)
                            print(name)
                prev_state[name] = is_pressed
            time.sleep(0.05)

controller_manager = ControllerManager()
