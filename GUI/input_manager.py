from raspi_control_modes import controller_manager
from headtrackingwithcam import HeadTracker

class InputManager:
    def __init__(self, queue = None):
        self.input_type = "controller"
        self.active = False
        self.tracker = None
        self.callback = None
        self.qRgb = queue

    def set_input_type(self, input_type):
        if input_type not in ["controller", "head"]:
            raise ValueError("Invalid input type")
        self.input_type = input_type

    def start(self, callback):
        self.stop()
        self.callback = callback
        self.active = True

        if self.input_type == "controller":
            controller_manager.start(callback)
        elif self.input_type == "head":
            self.tracker = HeadTracker(direction_callback=callback, queue=self.qRgb)
            self.tracker.start()

    def stop(self):
        if not self.active:
            return
        if self.input_type == "controller":
            controller_manager.stop()
        elif self.input_type == "head" and self.tracker:
            self.tracker.stop()
        self.active = False

input_manager = InputManager()
