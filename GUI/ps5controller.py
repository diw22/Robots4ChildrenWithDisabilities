import tkinter as tk
import pygame
import threading
import time

# Initialize pygame joystick
pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"[INFO] Controller: {joystick.get_name()}")

# GUI setup
root = tk.Tk()
root.title("PS5 Morse + D-Pad Control")
root.geometry("500x350")

morse_input = ""
label = tk.Label(root, text="Morse Code: ", font=("Helvetica", 20))
label.pack(pady=20)

status = tk.Label(root, text="Waiting for input...", font=("Helvetica", 16))
status.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=root.destroy)
exit_button.pack(pady=10)

# Morse code to action map
morse_command_map = {
    '.': "Wave",
    '-': "Fetch Toy",
    '.-': "Play Music",
    '--': "Rest Pose",
    '..': "Clap",
    '-.': "Spin Around"
}

def update_gui():
    label.config(text=f"Morse Code: {morse_input}")
    status.config(text="Typing...")

def submit_command():
    global morse_input
    command = morse_command_map.get(morse_input.strip(), "Unknown Command")
    status.config(text=f"Action: {command}")
    label.config(text=f"Executed: {command}")
    print(f"[INFO] Morse '{morse_input}' → {command}")
    morse_input = ""

def handle_dpad(x, y):
    if (x, y) == (0, 1):
        action = "Move Forward"
    elif (x, y) == (0, -1):
        action = "Move Backward"
    elif (x, y) == (-1, 0):
        action = "Turn Left"
    elif (x, y) == (1, 0):
        action = "Turn Right"
    else:
        return  # No direction pressed

    status.config(text=f"D-Pad: {action}")
    label.config(text=f"Manual Control: {action}")
    print(f"[D-PAD] {action}")

def controller_listener():
    global morse_input
    while True:
        pygame.event.pump()

        # Backspace with X button (assumed button 0)
        if joystick.get_button(0):
            if morse_input:
                morse_input = morse_input[:-1]
                update_gui()
            time.sleep(0.3)

        # Handle Morse buttons
        elif joystick.get_button(2):  # Circle → Dash
            morse_input += '-'
            update_gui()
            time.sleep(0.3)

        elif joystick.get_button(1):  # Cross → Dot
            morse_input += '.'
            update_gui()
            time.sleep(0.3)

        elif joystick.get_button(9):  # Options → Submit
            submit_command()
            time.sleep(0.3)

        elif joystick.get_button(3):  # Triangle → Exit
            print("[INFO] Exiting via Triangle")
            root.quit()
            break

        # Handle D-Pad as buttons (Windows PS5 controller)
        elif joystick.get_button(11):
            handle_dpad(0, 1)
        elif joystick.get_button(12):
            handle_dpad(0, -1)
        elif joystick.get_button(13):
            handle_dpad(-1, 0)
        elif joystick.get_button(14):
            handle_dpad(1, 0)

        time.sleep(0.05)

# Bind key press + start controller thread
root.bind("<KeyPress>", lambda event: None)  # placeholder if you want keyboard events too
threading.Thread(target=controller_listener, daemon=True).start()

root.mainloop()
