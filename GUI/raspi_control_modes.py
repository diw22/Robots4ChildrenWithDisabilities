# control_modes_basic.py

import pygame
import threading
import time
import platform

class ControllerManager:
    def __init__(self, device = "Windows"):
        self.thread = None
        self.running = False
        self.callback = None
        self.device = device

    def start(self, callback):
        self.callback = callback
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._controller_listener, daemon=True)
        self.thread.start()
        self.device = platform.system()
        print(self.device)

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

        if self.device == "Windows":
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

        else:
            button_map = {
                'Centre': 0,
                'Up': (0,1),
                'Down': (0,-1),
                'Left': (-1,0),
                'Right': (1,0)
            }
            cooldown = {name: 0 for name in button_map}
            while self.running:
                pygame.event.pump()
                for name, index in button_map.items():
                    is_pressed = False
                    if name == 'Centre':
                        is_pressed = joystick.get_button(index)
                    elif button_map[name] == joystick.get_hat(0):
                        is_pressed = True
                    

                    now = time.time()
                    if is_pressed and not prev_state[name] and now - cooldown[name] > 0.2:
                        cooldown[name] = now
                        if self.callback:
                                self.callback(name)
                                print(name)
                    prev_state[name] = is_pressed
                time.sleep(0.05)
             


controller_manager = ControllerManager()
