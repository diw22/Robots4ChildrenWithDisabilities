import pygame
import time



class XboxController:
    def __init__(self):
        self.CONTROLLER_AVAILABLE = True
        pygame.init()
        pygame.joystick.init()
        try:
            self.controller = pygame.joystick.Joystick(0)
            self.controller.init()
            print("Hi")
        except:
            print("Bye")
            self.CONTROLLER_AVAILABLE = False
            
        

        self.last_rotate_time = 0
        self.double_tap_threshold = 0.3  # seconds
        self.last_hat_x = 0
        self.last_tap_time = 0
        self.release_flag = True
        #pygame.event.pump()

    def get_key(self):
        key = None
        

        #self.last_hat_x = 0

        # D-pad input
        hat_x, hat_y = self.controller.get_hat(0)
        if hat_y == 1:
            key = "w"  # forward
        elif hat_y == -1:
            key = "s"  # backward
        elif hat_x == -1:
            key = "a"  # left
            self.release_flag = False
        elif hat_x == 1:
            key = "d"  # right
            self.release_flag = False

        # Double-tap logic for rotation
        if hat_x == 0:
            self.release_flag = True
        
        now = time.time()
        if hat_x != 0 and hat_x == self.last_hat_x and (abs(now - self.last_tap_time)) < self.double_tap_threshold:
            if hat_x == -1:
                key = "z"  # rotate left
            elif hat_x == 1:
                key = "x"  # rotate right
        elif hat_x != 0:
            if not(self.release_flag):
                self.last_tap_time = time.time()
                self.release_flag = False
        self.last_hat_x = hat_x

        # Buttons
        if self.controller.get_button(0):  # A
            key = "r"  # speed up
        elif self.controller.get_button(1):  # B
            key = "f"  # speed down
        elif self.controller.get_button(7):  # Menu
            key = "q"  # quit

        return key

 