from gpiozero import Button, Robot
from time import time

robot = Robot(left=(7, 8), right=(9, 10))
button = Button(2)  # GPIO pin 2

press_start = 0

def on_press():
    global press_start
    press_start = time()

def on_release():
    global press_start
    duration = time() - press_start
    if duration < 1:  # Short press: Forward
        robot.forward()
    elif 1 <= duration < 3:  # Long press: Stop
        robot.stop()
    else:  # Extra-long press: Backward
        robot.backward()

button.when_pressed = on_press
button.when_released = on_release

# Keep the program running
while True:
    pass