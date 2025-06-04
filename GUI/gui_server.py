import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QMessageBox, QSpacerItem,
                             QSizePolicy, QStackedWidget)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon, QMovie
from PyQt5.QtCore import Qt, QSize, QTimer, QMetaObject, Q_ARG
from control_modes_basic import controller_manager
import threading
import requests
import socket
import threading
from input_manager import InputManager
import depthai as dai
from headtrackingwithcam import HeadTracker

class MainMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.game_widget = None
        self.message_widget = None
        self.dice_widget = None
        self.setWindowTitle("Main Menu")
        self.setGeometry(0, 0, 1920, 1080)

        self.set_background("GUI_background.png")

        layout = QVBoxLayout()
        layout.addSpacerItem(QSpacerItem(20, int(self.height() * 2/3), QSizePolicy.Minimum, QSizePolicy.Expanding))

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignHCenter)

        self.buttons = []
        self.selected_index = 0

        self.btn_ttt = QPushButton()
        self.btn_ttt.setIcon(QIcon("tictactoe_button.png"))
        self.btn_ttt.setIconSize(QSize(350, 350))
        self.btn_ttt.setFlat(True)
        self.btn_ttt.clicked.connect(self.start_tic_tac_toe)
        self.buttons.append(self.btn_ttt)
        button_layout.addWidget(self.btn_ttt)

        self.btn_msg = QPushButton()
        self.btn_msg.setIcon(QIcon("message_button.png"))
        self.btn_msg.setIconSize(QSize(350, 350))
        self.btn_msg.setFlat(True)
        self.btn_msg.clicked.connect(self.start_message_menu)
        self.buttons.append(self.btn_msg)
        button_layout.addWidget(self.btn_msg)

        self.btn_clean = QPushButton()
        self.btn_clean.setIcon(QIcon("tidyup_button.png"))
        self.btn_clean.setIconSize(QSize(350, 350))
        self.btn_clean.setFlat(True)
        self.btn_clean.clicked.connect(lambda: QMessageBox.information(self, "Tidy", "Tidying up..."))
        self.buttons.append(self.btn_clean)
        button_layout.addWidget(self.btn_clean)
        
        self.btn_dice = QPushButton()
        self.btn_dice.setIcon(QIcon("tidyup_button.png"))
        self.btn_dice.setIconSize(QSize(350, 350))
        self.btn_dice.setFlat(True)
        #self.btn_dice.clicked.connect(self.start_dice_game)
        self.buttons.append(self.btn_dice)
        button_layout.addWidget(self.btn_dice)
        self.button_icons = {
            self.btn_ttt: {
                "normal": QIcon("tictactoe_button.png"),
                "highlight": QIcon("highlight_tictactoe_button.png")
            },
            self.btn_msg: {
                "normal": QIcon("message_button.png"),
                "highlight": QIcon("highlight_message_button.png")
            },
            self.btn_clean: {
                "normal": QIcon("tidyup_button.png"),
                "highlight": QIcon("highlight_tidy_button.png")
            },
            self.btn_dice: {
                "normal": QIcon("dice_button.png"),
                "highlight": QIcon("highlight_dice_button.png")
            }
        }
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.highlight_selected()
    
        input_manager.start(self.handle_direction)
    def highlight_selected(self):
        for i, btn in enumerate(self.buttons):
            icon_type = "highlight" if i == self.selected_index else "normal"
            btn.setIcon(self.button_icons[btn][icon_type])

    def handle_direction(self, direction):
        if direction == "Left":
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
            self.highlight_selected()
        elif direction == "Right":
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
            self.highlight_selected()
        elif direction == "Centre":
            self.buttons[self.selected_index].click()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.handle_direction("Left")
        elif key == Qt.Key_Right:
            self.handle_direction("Right")
        elif key == Qt.Key_Space:
            self.handle_direction("Centre")

    def start_tic_tac_toe(self):
        input_manager.stop()
        self.stacked_widget.setCurrentWidget(self.game_widget)
        self.game_widget.activate_controller()
    def set_message_widget(self, message_widget):
        self.message_widget = message_widget
    
    def start_dice(self):
        input_manager.stop()
        self.stacked_widget.setCurrentWidget(self.dice_widget)
        self.dice_widget.activate_controller()
    def set_dice_widget(self, dice_widget):
        self.dice_widget = dice_widget
    
    def start_message_menu(self):
        input_manager.stop()
        self.stacked_widget.setCurrentWidget(self.message_widget)
        self.message_widget.activate_controller()

    def set_background(self, image_path):
        self.setAutoFillBackground(True)
        background = QPixmap(image_path)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

    def set_game_widget(self, game_widget):
        self.game_widget = game_widget
        
    def activate_controller(self):
        input_manager.start(self.handle_direction)
    
    def activate_controller(self):
        self.setFocus()
        input_manager.start(self.handle_direction)
        
class TicTacToe(QWidget):
    def set_background(self, image_path):
        self.setAutoFillBackground(True)
        background = QPixmap(image_path)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

    def back_to_menu(self):
        from control_modes_basic import controller_manager
        input_manager.stop()
        self.stacked_widget.setCurrentIndex(0)
        self.close_connection()
        self.stacked_widget.currentWidget().activate_controller()
    def __init__(self, stacked_widget, is_server=False, server_ip=None, port=XXXXX):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.is_server = is_server
        self.port = port
        self.sock = None

        self.board = [''] * 9
        self.selected_index = 0
        self.buttons = []
        self.turn = 'X'

        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Tic-Tac-Toe")
        self.setGeometry(0, 0, 1920, 1080)
        self.set_background("tictac_background.png")

        self.turn = 'X'
        self.board = [''] * 9
        self.buttons = []
        self.selected_index = 0

        main_layout = QVBoxLayout()
        top_spacer = QSpacerItem(20, self.height() // 3, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addSpacerItem(top_spacer)

        back_button = QPushButton("← Back to Menu")
        back_button.setFixedSize(200, 50)
        back_button.clicked.connect(self.back_to_menu)
        back_button.setStyleSheet("font-size: 18px; padding: 5px;")
        main_layout.addWidget(back_button, alignment=Qt.AlignLeft)

        for i in range(3):
            row_layout = QHBoxLayout()
            for j in range(3):
                idx = i * 3 + j
                btn = QPushButton()
                btn.setFixedSize(250, 250)
                btn.setIcon(QIcon("emptybox.png"))
                btn.setIconSize(QSize(250, 250))
                btn.setFlat(True)
                btn.setStyleSheet("background-color: rgba(0, 0, 0, 0); border: none;")
                btn.clicked.connect(lambda checked, idx=idx: self.make_move(idx))
                self.buttons.append(btn)
                row_layout.addWidget(btn)
            main_layout.addLayout(row_layout)
        
        self.button_icons = {
            '': {
                "normal": QIcon("emptybox.png"),
                "highlight": QIcon("highlight_emptybox.png")
            },
            'X': {
                "normal": QIcon("crossbox.png"),
                "highlight": QIcon("highlight_crossbox.png")
            },
            'O': {
                "normal": QIcon("noughtbox.png"),
                "highlight": QIcon("highlight_noughtbox.png")
            }
        }
        self.setLayout(main_layout)
        self.highlight_selected()
        if is_server:
            threading.Thread(target=self.start_server, daemon=True).start()
        elif server_ip:
            self.connect_to_server(server_ip)
    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("0.0.0.0", self.port))
        server_socket.listen(1)
        print("Waiting for client...")
        conn, addr = server_socket.accept()
        print(f"Connected to {addr}")
        self.sock = conn

        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                print("Received:", data)
                self.apply_remote_move(data)
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.close_connection()

    def connect_to_server(self, ip, port=None):
        port = port or self.port
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((ip, port))
            print("Connected to server.")
        except Exception as e:
            print(f"Client connection error: {e}")
            self.sock = None

    
    def activate_controller(self):
        from control_modes_basic import controller_manager
        input_manager.start(self.handle_direction)
    def highlight_selected(self):
        for i, btn in enumerate(self.buttons):
            cell_value = self.board[i]  # '', 'X', or 'O'
            icon_type = "highlight" if i == self.selected_index else "normal"
            btn.setIcon(self.button_icons[cell_value][icon_type])
            
    def handle_direction(self, direction):
        if direction == "Left":
            self.selected_index = (self.selected_index - 1) % 9
        elif direction == "Right":
            self.selected_index = (self.selected_index + 1) % 9
        elif direction == "Centre":
            self.make_move(self.selected_index)

        self.highlight_selected()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.handle_direction("Left")
        elif key == Qt.Key_Right:
            self.handle_direction("Right")
        elif key == Qt.Key_Up:
            self.handle_direction("Up")
        elif key == Qt.Key_Down:
            self.handle_direction("Down")
        elif key == Qt.Key_Space:
            self.handle_direction("Centre")

    def make_move(self, idx):
        if self.board[idx] == '':
            self.board[idx] = 'X'
            self.send_move_to_server('X', idx)
            self.highlight_selected()
            row = idx // 3  # e.g., 5 // 3 = 1 (second row)
            col = idx % 3 
            move_str = f"X:{chr(65 + row)}{col + 1}"

            if self.sock:
                try:
                    self.sock.send(move_str.encode())
                except Exception as e:
                    print(f"Send error: {e}")
            if self.check_winner('X'):
                QTimer.singleShot(0, lambda: QMessageBox.information(self, "Game Over", "You win!"))
                self.reset_game()
                return
            QTimer.singleShot(0, self.delayed_computer_move)


    def delayed_computer_move(self):
        QTimer.singleShot(500, self.computer_move)
    def close_connection(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.sock.close()
            except Exception:
                pass
            print("Socket closed.")
            self.sock = None
    def activate_controller(self):
        self.setFocus()
        input_manager.start(self.handle_direction)
    def computer_move(self):
        for idx in range(9):
            if self.board[idx] == '':
                self.board[idx] = 'O'
                self.send_move_to_server('O', best_move)
                self.highlight_selected()
                if self.check_winner('O'):
                    QTimer.singleShot(0, lambda: QMessageBox.information(self, "Game Over", "Computer wins!"))
                    self.reset_game()
                return
    def send_move_to_server(self, player, move_index):
        data = {
            "player": player,
            "move": move_index,
            "board": self.board.copy()
        }
        print(f"[Simulated POST] {data}")

    def check_winner(self, player):
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        return any(self.board[a]==player and self.board[b]==player and self.board[c]==player for a,b,c in wins)

    def reset_game(self):
        self.board = [''] * 9
        self.selected_index = 0
        self.highlight_selected()

class MessageWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Send Message")
        self.setGeometry(0, 0, 1920, 1080)
        self.set_background("message_background.png")

        self.selected_index = 0
        self.buttons = []

        layout = QVBoxLayout()

        back_button = QPushButton("← Back to Menu")
        back_button.setFixedSize(200, 50)
        back_button.clicked.connect(self.back_to_menu)
        back_button.setStyleSheet("font-size: 18px; padding: 5px;")
        layout.addWidget(back_button, alignment=Qt.AlignLeft)

        for i in range(2):
            row_layout = QHBoxLayout()
            for j in range(2):
                idx = i * 2 + j
                btn = QPushButton()
                btn.setFixedSize(600, 600)
                btn.setIcon(QIcon(f"message_{idx}.png")) 
                btn.setIconSize(QSize(600, 600))
                btn.setFlat(True)
                btn.clicked.connect(lambda checked, idx=idx: self.send_message(idx))
                self.buttons.append(btn)
                row_layout.addWidget(btn)
            layout.addLayout(row_layout)

        self.setLayout(layout)
        self.highlight_selected()

    def set_background(self, image_path):
        self.setAutoFillBackground(True)
        background = QPixmap(image_path)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)

    def back_to_menu(self):
        input_manager.stop()
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.currentWidget().activate_controller()

    def handle_direction(self, direction):
        if direction == "Left":
            self.selected_index = (self.selected_index - 1) % 4
        elif direction == "Right":
            self.selected_index = (self.selected_index + 1) % 4
        elif direction == "Centre":
            self.send_message(self.selected_index)
        self.highlight_selected()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left:
            self.handle_direction("Left")
        elif key == Qt.Key_Right:
            self.handle_direction("Right")
        elif key == Qt.Key_Space:
            self.handle_direction("Centre")

    def highlight_selected(self):
        for i, btn in enumerate(self.buttons):
            size = QSize(200, 200)
            icon_path = f"emptybox.png"
            if i == self.selected_index:
                icon_path = f"highlight_emptybox.png"
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(size)

    def send_message(self, idx):
        QMessageBox.information(self, "Message Sent", f"Message {idx + 1} sent!")

    def activate_controller(self):
        self.setFocus()
        input_manager.start(self.handle_direction)


class DiceWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Dice Game")
        self.setGeometry(0, 0, 1920, 1080)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        #Define paths to animations
        self.idle_animation_path = "animation_0.gif"
        self.transition_animation_path = "transition.gif"
        self.action_animations = {
            Qt.Key_D: "animation_1.gif",
            Qt.Key_W: "animation_2.gif",
            Qt.Key_A: "animation_3.gif",
            Qt.Key_S: "animation_4.gif"
        }

        self.current_movie = None
        self.play_animation(self.idle_animation_path)

    def keyPressEvent(self, event):
        key = event.key()
        if key in self.action_animations:
            self.play_transition_then_action(self.action_animations[key])

    def play_animation(self, gif_path):
        if self.current_movie:
            self.current_movie.stop()
            self.label.clear()
        self.current_movie = QMovie(gif_path)
        self.label.setMovie(self.current_movie)
        self.current_movie.start()

    def play_transition_then_action(self, action_gif_path):
        self.play_animation(self.transition_animation_path)
        QTimer.singleShot(2000, lambda: self.play_animation(action_gif_path))

headtrack = False

if headtrack:
    # -------------------- CAMERA SETUP ---------------------
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define source and output
    camRgb = pipeline.create(dai.node.ColorCamera)
    xoutRgb = pipeline.create(dai.node.XLinkOut)

    xoutRgb.setStreamName("rgb")

    # Properties
    camRgb.setPreviewSize(500, 500)
    camRgb.setInterleaved(False)
    camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.RGB)

    # Linking
    camRgb.preview.link(xoutRgb.input)


    with dai.Device(pipeline) as device:
        print('Connected cameras:', device.getConnectedCameraFeatures())
        # Print out usb speed
        print('Usb speed:', device.getUsbSpeed().name)
        # Bootloader version
        if device.getBootloaderVersion() is not None:
            print('Bootloader version:', device.getBootloaderVersion())
        # Device name
        print('Device name:', device.getDeviceName(), ' Product name:', device.getProductName())

        # Output queue will be used to get the rgb frames from the output defined above
        qRgb = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)

        input_manager = InputManager(queue = qRgb)
        if __name__ == '__main__':
            input_manager.set_input_type("head")
            app = QApplication(sys.argv)
            stacked_widget = QStackedWidget()

            menu = MainMenu(stacked_widget)
            game = TicTacToe(stacked_widget)
            message_widget = MessageWidget(stacked_widget)

            stacked_widget.addWidget(menu)
            stacked_widget.addWidget(game)
            stacked_widget.addWidget(message_widget)

            menu.set_game_widget(game)
            menu.set_message_widget(message_widget)

            stacked_widget.setCurrentWidget(menu)
            stacked_widget.showFullScreen()

            sys.exit(app.exec_())

else:
    input_manager = InputManager()
    if __name__ == '__main__':
        input_manager.set_input_type("controller")
        app = QApplication(sys.argv)
        stacked_widget = QStackedWidget()

        menu = MainMenu(stacked_widget)
        game = TicTacToe(stacked_widget)
        message_widget = MessageWidget(stacked_widget)

        stacked_widget.addWidget(menu)
        stacked_widget.addWidget(game)
        stacked_widget.addWidget(message_widget)

        menu.set_game_widget(game)
        menu.set_message_widget(message_widget)

        stacked_widget.setCurrentWidget(menu)
        stacked_widget.showFullScreen()

        sys.exit(app.exec_())