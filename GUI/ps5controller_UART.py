import tkinter as tk
import pygame
import threading
import time
import serial

# === UART Setup for Raspberry Pi ===
try:
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    print("[UART] Serial connection established on /dev/serial0")
except Exception as e:
    ser = None
    print(f"[UART ERROR] Could not open serial port: {e}")

# === Pygame Controller Setup ===
pygame.init()
pygame.joystick.init()

joystick = pygame.joystick.Joystick(0)
joystick.init()
print(f"[INFO] Controller: {joystick.get_name()}")

# === GUI Setup ===
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

# === Morse Code Mapping ===
morse_command_map = {
    '.': "Wave",
    '-': "Fetch Toy",
    '.-': "Play Music",
    '--': "Rest Pose",
    '..': "Clap",
    '-.': "Spin Around"
}

# === Helper: Update GUI Display ===
def update_gui():
    label.config(text=f"Morse Code: {morse_input}")
    status.config(text="Typing...")

# === Helper: Send UART ===
def send_uart(message):
    if ser:
        try:
            ser.write((message + '\n').encode())
            print(f"[UART] Sent: {message}")
        except Exception as e:
            print(f"[UART ERROR] {e}")
    else:
        print(f"[UART] (skipped) {message}")

# === Submit Morse Input ===
def submit_command():
    global morse_input
    command = morse_command_map.get(morse_input.strip(), "Unknown Command")
    status.config(text=f"Action: {command}")
    label.config(text=f"Executed: {command}")
    print(f"[INFO] Morse '{morse_input}' → {command}")
    send_uart(command)
    morse_input = ""

# === Handle D-Pad Actions ===
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
        return

    status.config(text=f"D-Pad: {action}")
    label.config(text=f"Manual Control: {action}")
    print(f"[D-PAD] {action}")
    send_uart(action)

# === Controller Listener Thread ===
def controller_listener():
    global morse_input
    while True:
        pygame.event.pump()

        # X Button (assumed button 0) = Backspace
        if joystick.get_button(0):
            if morse_input:
                morse_input = morse_input[:-1]
                update_gui()
            time.sleep(0.3)

        # Circle → Dash
        elif joystick.get_button(2):
            morse_input += '-'
            update_gui()
            time.sleep(0.3)

        # Cross → Dot
        elif joystick.get_button(1):
            morse_input += '.'
            update_gui()
            time.sleep(0.3)

        # Options → Submit
        elif joystick.get_button(9):
            submit_command()
            time.sleep(0.3)

        # Triangle → Exit
        elif joystick.get_button(3):
            print("[INFO] Exiting via Triangle")
            root.quit()
            break

        # D-Pad (as buttons)
        elif joystick.get_button(11):
            handle_dpad(0, 1)
        elif joystick.get_button(12):
            handle_dpad(0, -1)
        elif joystick.get_button(13):
            handle_dpad(-1, 0)
        elif joystick.get_button(14):
            handle_dpad(1, 0)

        time.sleep(0.05)

# === Launch Controller Thread and Start GUI ===
root.bind("<KeyPress>", lambda event: None)
threading.Thread(target=controller_listener, daemon=True).start()
root.mainloop()


#Pin 8 (GPIO14 TXD)  = RX on device
#Pin 10 (GPIO15 RXD) = TX on device
