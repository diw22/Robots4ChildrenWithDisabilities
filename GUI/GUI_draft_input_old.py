import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QMessageBox, QSpacerItem,
                             QSizePolicy, QStackedWidget)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QMetaObject, Q_ARG
from control_modes_basic import controller_manager
import threading
import requests
import zmq
import random
import queue
import json

from input_manager import input_manager
#from head_tracker import HeadTracker
#from input_manager import input_manager

class MainMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        
        self.input_mode = "controller"
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.game_widget = None
        self.setWindowTitle("Main Menu")
        self.setGeometry(0, 0, 1920, 1080)

        self.set_background("GUI_background.png")

        layout = QVBoxLayout()

        top_bar_layout = QHBoxLayout()
        top_bar_layout.addStretch()
        
        self.input_mode_button = QPushButton()
        self.input_mode_button.setIcon(QIcon("controller_toggle_button.png"))
        self.input_mode_button.setIconSize(QSize(350, 350))
        self.input_mode_button.setFlat(True)
        self.input_mode_button.clicked.connect(self.toggle_input_mode)
        
        top_bar_layout.addWidget(self.input_mode_button)
        layout.addLayout(top_bar_layout)

        # Spacer to push main buttons down
        layout.addSpacerItem(QSpacerItem(20, int(self.height() * 2/3), QSizePolicy.Minimum, QSizePolicy.Expanding))


        
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignHCenter)
        layout.addLayout(button_layout)
        
        self.buttons = []
        self.selected_index = 1
        
        self.buttons.insert(0, self.input_mode_button)

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
        self.btn_clean.clicked.connect(self.send_tidy_command)
        self.buttons.append(self.btn_clean)
        button_layout.addWidget(self.btn_clean)

        self.btn_free_roam = QPushButton()
        self.btn_free_roam.setIcon(QIcon("free_button.png"))
        self.btn_free_roam.setIconSize(QSize(350, 350))
        self.btn_free_roam.setFlat(True)
        self.btn_free_roam.clicked.connect(self.start_free_roam)
        self.buttons.append(self.btn_free_roam)
        button_layout.addWidget(self.btn_free_roam)
        
        self.button_icons = {
            self.input_mode_button: {
                "controller": {
                    "normal": QIcon("controller_toggle_button.png"),
                    "highlight": QIcon("highlight_controller_toggle_button.png")
                },
                "headtracking": {
                    "normal": QIcon("headtracking_toggle_button.png"),
                    "highlight": QIcon("highlight_headtracking_toggle_button.png")
                }
            },
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
            self.btn_free_roam: {
                "normal": QIcon("free_button.png"),
                "highlight": QIcon("highlight_free_button.png")
                }
        }

        
        
        self.setLayout(layout)
        self.highlight_selected()
        

        input_manager.start(self.handle_direction)
    def set_message_widget(self, message_widget):
            self.message_widget = message_widget
            
    def tidy_function(self):
        
        
        tidy_done = False
        
        context = zmq.Context()
        
        receive_socket = context.socket(zmq.PULL)
        receive_socket.connect("tcp://192.168.137.109:5555")
        receive_socket.setsockopt(zmq.CONFLATE, 1)
        socket = context.socket(zmq.PUSH)
        socket.connect("tcp://192.168.137.109:5556") 
        socket.setsockopt(zmq.CONFLATE, 1)
        socket.send_string(json.dumps("start"))
        print("[INFO] Sent 'start' to port 5556")
        #start waiting for message
        while not tidy_done:
            try:
                message = receive_socket.recv_string(flags=zmq.NOBLOCK)
                data = json.loads(message)
                if data == "stop":
                    tidy_done = True
                    print("[INFO] Tidy command completed.")
                    break
            except zmq.Again:
                pass
        

        
    def toggle_input_mode(self):
        self.input_mode = "headtracking" if self.input_mode == "controller" else "controller"
        self.highlight_selected()
    def set_free_roam_widget(self, free_roam_widget):
            self.free_roam_widget = free_roam_widget
    def set_motor_roam_widget(self, motor_roam_widget):
            self.motor_roam_widget = motor_roam_widget
    def start_message_menu(self):
            input_manager.stop()
            self.stacked_widget.setCurrentWidget(self.message_widget)
            self.message_widget.activate_controller()
    
    def start_motor_roam(self):
            input_manager.stop()
            self.stacked_widget.setCurrentWidget(self.motor_roam_widget)
            self.motor_roam_widget.activate_controller()
    def start_free_roam(self):
            input_manager.stop()
            self.stacked_widget.setCurrentWidget(self.free_roam_widget)
            self.free_roam_widget.activate_controller()
        
    def highlight_selected(self):
        for i, btn in enumerate(self.buttons):
            is_selected = (i == self.selected_index)
            if btn == self.input_mode_button:
                mode = self.input_mode
                icon_type = "highlight" if is_selected else "normal"
                btn.setIcon(self.button_icons[btn][mode][icon_type])
            else:
                icon_type = "highlight" if is_selected else "normal"
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
    def set_message_widget(self, message_widget):
            self.message_widget = message_widget
class TicTacToe(QWidget):
    def set_background(self, image_path):
        self.setAutoFillBackground(True)
        background = QPixmap(image_path)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)
    def send_move_to_server(self, player, move_index):
        data = {
            "player": player,
            "move": move_index,
            "board": self.board.copy()
        }
        print(f"[Simulated POST] {data}")
    def back_to_menu(self):
        from control_modes_basic import controller_manager
        input_manager.stop()
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.currentWidget().activate_controller()
        print(self.selected_index_ttt)

    def __init__(self, stacked_widget):
        super().__init__()
        self.game_over = False
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Tic-Tac-Toe")
        self.setGeometry(0, 0, 1920, 1080)
        self.set_background("tictac_background.png")

        self.game_count = 0
        self.turn = 'X'
        self.board = [''] * 9
        self.buttons = []
        self.selected_index_ttt = 1

        main_layout = QVBoxLayout()
        top_spacer = QSpacerItem(20, self.height() // 3, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addSpacerItem(top_spacer)

        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("backmenu.png"))
        self.back_button.setIconSize(QSize(250, 250))
        self.back_button.setFlat(True)
        self.back_button.clicked.connect(self.back_to_menu)
        #back_button.setStyleSheet("font-size: 18px; padding: 5px;")

        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()
        main_layout.addLayout(top_row)

        self.buttons.append(self.back_button)
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
            },
        }
        self.button_icons[self.back_button] = {
            "normal": QIcon("backmenu.png"),
            "highlight": QIcon("highlight_backmenu_button.png")
        }
        self.setLayout(main_layout)

        self.highlight_selected()
        
    def show_game_result(self, result):
        self.board = [''] * 9
        self.highlight_selected()
        self.game_over = True

        # Hide all buttons
        for btn in self.buttons:
            btn.hide()

        # Change background
        if result == "win":
            self.set_background("you_win.png")
        elif result == "lose":
            self.set_background("you_lose.png")
        elif result == "draw":
            self.set_background("draw.png")

    def activate_controller(self):
        from control_modes_basic import controller_manager
        input_manager.start(self.handle_direction)
    def highlight_selected(self):
        for i, btn in enumerate(self.buttons):
            if btn == self.back_button:
                icon_type = "highlight" if i == self.selected_index_ttt else "normal"
                btn.setIcon(self.button_icons[btn][icon_type])
            else:
                cell_index = i - 1
                cell_value = self.board[cell_index]
                icon_type = "highlight" if i == self.selected_index_ttt else "normal"
                btn.setIcon(self.button_icons[cell_value][icon_type]) 
    def handle_direction(self, direction):
        if self.game_over:
            self.reset_game()
            return

        if direction == "Left":
            self.selected_index_ttt = (self.selected_index_ttt - 1) % len(self.buttons)
        elif direction == "Right":
            self.selected_index_ttt = (self.selected_index_ttt + 1) % len(self.buttons)
        elif direction == "Centre":
            if self.selected_index_ttt == 0:
                self.back_button.click()
            else:
                self.make_move(self.selected_index_ttt - 1) 

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
            if self.check_winner('X'):
                QTimer.singleShot(0, lambda: self.show_game_result("win"))
                return
            elif self.check_draw():
                QTimer.singleShot(0, lambda: self.show_game_result("draw"))
                return
            QTimer.singleShot(0, self.delayed_computer_move)


    def delayed_computer_move(self):
        QTimer.singleShot(500, self.computer_move)
    
    def activate_controller(self):
        self.setFocus()
        input_manager.start(self.handle_direction)
        
    def check_draw(self):
        return '' not in self.board and self.get_winner(self.board) is None

    def computer_move(self):
        if self.game_count % 2 == 1:
            available_moves = [i for i in range(9) if self.board[i] == '']
            if available_moves:
                move = random.choice(available_moves)
                self.board[move] = 'O'
                self.send_move_to_server('O', move)
                self.highlight_selected()
                if self.check_winner('O'):
                    QMetaObject.invokeMethod(self, lambda: self.show_game_result("lose"), Qt.QueuedConnection)
                elif self.check_draw():
                    QMetaObject.invokeMethod(self, lambda: self.show_game_result("draw"), Qt.QueuedConnection)
            return

        def minimax(board, depth, is_maximizing):
            winner = self.get_winner(board)
            if winner == 'O':
                return 1
            elif winner == 'X':
                return -1
            elif '' not in board:
                return 0

            if is_maximizing:
                best_score = -float('inf')
                for i in range(9):
                    if board[i] == '':
                        board[i] = 'O'
                        score = minimax(board, depth + 1, False)
                        board[i] = ''
                        best_score = max(score, best_score)
                return best_score
            else:
                best_score = float('inf')
                for i in range(9):
                    if board[i] == '':
                        board[i] = 'X'
                        score = minimax(board, depth + 1, True)
                        board[i] = ''
                        best_score = min(score, best_score)
                return best_score

        best_score = -float('inf')
        best_move = None
        for i in range(9):
            if self.board[i] == '':
                self.board[i] = 'O'
                score = minimax(self.board, 0, False)
                self.board[i] = ''
                if score > best_score:
                    best_score = score
                    best_move = i

        if best_move is not None:
            self.board[best_move] = 'O'
            self.send_move_to_server('O', best_move)
            self.highlight_selected()
            if self.check_winner('O'):
                QTimer.singleShot(0, lambda: self.show_game_result("lose"))
            elif self.check_draw():
                QTimer.singleShot(0, lambda: self.show_game_result("draw"))
    def check_winner(self, player):
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        return any(self.board[a]==player and self.board[b]==player and self.board[c]==player for a,b,c in wins)
    def get_winner(self, board):
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None
    def reset_game(self):
        self.set_background("tictac_background.png")
        self.board = [''] * 9
        self.selected_index_ttt = 1
        self.game_over = False
        self.game_count += 1

        for btn in self.buttons:
            btn.show()

        self.highlight_selected()
    
class MessageWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Send Message")
        self.setGeometry(0, 0, 1920, 1080)
        self.set_background("message_background.png")

        self.game_over = False
        
        self.selected_index_message = 1
        self.buttons = []
        self.button_icons = {}
        
        layout = QVBoxLayout()
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("backmenu.png"))
        self.back_button.setIconSize(QSize(250, 250))
        self.back_button.setFlat(True)
        self.back_button.clicked.connect(self.back_to_menu)
        #back_button.setStyleSheet("font-size: 18px; padding: 5px;")
        self.buttons.append(self.back_button)
        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()
        layout.addLayout(top_row)
        
        for i in range(2):
            row_layout = QHBoxLayout()
            for j in range(2):
                idx = i * 2 + j
                btn = QPushButton()
                btn.setFixedSize(350, 350)
                btn.setIcon(QIcon(f"message_{idx}.png")) 
                btn.setIconSize(QSize(350, 350))
                btn.setFlat(True)
                btn.clicked.connect(lambda checked, idx=idx: self.send_message(idx))
                self.buttons.append(btn)
                row_layout.addWidget(btn)
            layout.addLayout(row_layout)
            
        icons = [
            ("backmenu.png", "highlight_backmenu_button.png"),
            ("hibox.png", "highlight_hibox.png"),
            ("lets_playbox.png", "highlight_lets_playbox.png"),
            ("howareyoubox.png", "highlight_howareyoubox.png"),
            ("howwasyourdaybox.png", "highlight_howwasyourdaybox.png")
           
        ]

        for i in range(5):
            self.button_icons[self.buttons[i]] = {
                "normal": QIcon(icons[i][0]),
                "highlight": QIcon(icons[i][1])
            }

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
        if self.game_over:
            self.reset_game()
            return
        else:
            if direction == "Left":
                self.selected_index_message = (self.selected_index_message - 1) % len(self.buttons)
            elif direction == "Right":
                self.selected_index_message = (self.selected_index_message + 1) % len(self.buttons)

            elif direction == "Centre":
                if self.selected_index_message == 0:
                    self.back_button.click()
                else:
                    self.send_message(self.selected_index_message)
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
            icon_type = "highlight" if i == self.selected_index_message else "normal"
            if btn in self.button_icons:
                btn.setIcon(self.button_icons[btn][icon_type])
    def reset_game(self):
        self.set_background("message_background.png")
        self.selected_index_message = 1
        self.game_over = False

        for btn in self.buttons:
            btn.show()

        self.highlight_selected()
    def send_message(self, idx):
        
        for btn in self.buttons:
            btn.hide()
        self.set_background(f"message_{idx}_background.png")
        self.game_over = True
        print(f"[INFO] Displaying message {idx} ...")
        

    def activate_controller(self):
        self.setFocus()
        input_manager.start(self.handle_direction)


class FreeRoamWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.control_mode = "menu"
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Free Roam")
        self.setGeometry(0, 0, 1920, 1080)
        self.set_background("freeroamback.png")

        self.selected_index_freeroam = 1
        self.buttons = []
        self.button_icons = {}

        layout = QVBoxLayout()
        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("backmenu.png"))
        self.back_button.setIconSize(QSize(250, 250))
        self.back_button.setFlat(True)
        self.back_button.clicked.connect(self.back_to_menu)

        self.toggle_button = QPushButton()
        self.toggle_button.setIcon(QIcon("arm_button.png"))
        self.toggle_button.setIconSize(QSize(250, 250))
        self.toggle_button.setFlat(True)
        self.toggle_button.clicked.connect(self.toggle_control_mode)

        self.buttons.append(self.toggle_button)
        self.button_icons[self.toggle_button] = {
            "menu": {
                "normal": QIcon("menucontrol_button.png"),
                "highlight": QIcon("highlight_menucontrol_button.png")
            },
            "free": {
                "normal": QIcon("arm_button.png"),
                "highlight": QIcon("highlight_arm_button.png")
            },
            "motor": {
                "normal": QIcon("motor_button.png"),
                "highlight": QIcon("highlight_motor_button.png")
            }
        }
        top_row = QHBoxLayout()
        top_row.addWidget(self.back_button)
        top_row.addStretch()
        top_row.addWidget(self.toggle_button)
        layout.addLayout(top_row)
        

        self.buttons.append(self.back_button)
        self.button_icons[self.back_button] = {
            "normal": QIcon("backmenu.png"),
            "highlight": QIcon("highlight_backmenu_button.png")
        }

        

        self.setLayout(layout)
        self.highlight_selected()

    
    def back_to_menu(self):
        from draft_ps5_control_thread import stop_ps5_control
        stop_ps5_control()    
        input_manager.start(self.stacked_widget.currentWidget().handle_direction)
        self.stacked_widget.setCurrentIndex(0)
        self.stacked_widget.currentWidget().activate_controller()
        
    def toggle_control_mode(self):
        if self.control_mode == "menu":
            from draft_ps5_control_thread import start_ps5_control
            start_ps5_control()
            self.control_mode = "free"

        elif self.control_mode == "free":
            from draft_ps5_control_thread import stop_ps5_control
            stop_ps5_control()

            from motor_roam_control import start_motor_roam_control
            start_motor_roam_control()
            self.control_mode = "motor"

        elif self.control_mode == "motor":
            from motor_roam_control import stop_motor_roam_control
            stop_motor_roam_control()
            self.control_mode = "menu"

        print(f"[INFO] Switched to {self.control_mode} control.")
        self.highlight_selected()

    def set_background(self, image_path):
        self.setAutoFillBackground(True)
        background = QPixmap(image_path)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)



    def handle_direction(self, direction):
        if direction == "Left":
            self.selected_index_freeroam = (self.selected_index_freeroam - 1) % len(self.buttons)
        elif direction == "Right":
            self.selected_index_freeroam = (self.selected_index_freeroam + 1) % len(self.buttons)
        elif direction == "Centre":
            self.buttons[self.selected_index_freeroam].click()
        self.highlight_selected()

    def highlight_selected(self):
        for i, btn in enumerate(self.buttons):
            icon_type = "highlight" if i == self.selected_index_freeroam else "normal"
            if btn == self.toggle_button:
                mode = self.control_mode
                btn.setIcon(self.button_icons[btn][mode][icon_type])
            else:
                btn.setIcon(self.button_icons[btn][icon_type])
    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Left or key == Qt.Key_Right:
            self.handle_direction("Left")
        elif key == Qt.Key_Space:
            self.handle_direction("Centre")

    def activate_controller(self):
        input_manager.stop()
        if self.control_mode == "free":
            from draft_ps5_control_thread import start_ps5_control
            start_ps5_control()
            print("[INFO] Free control activated.")
        elif self.control_mode == "motor":
            from motor_roam_control import start_motor_roam_control
            start_motor_roam_control()
            print("[INFO] Motor control activated.")
        else:
            print("[INFO] Menu mode: no robot control active.")
        #button 7 or 10 back to main menu

#class MotorRoamWidget(QWidget):
#    def __init__(self, stacked_widget):
#        super().__init__()
#        self.setFocusPolicy(Qt.StrongFocus)
#        self.stacked_widget = stacked_widget
#        self.setWindowTitle("Motor Roam")
#        self.setGeometry(0, 0, 1920, 1080)
#        self.set_background("freeroamback.png")
#
#        self.selected_index = 0
#        self.buttons = []
#        self.button_icons = {}
#
#        layout = QVBoxLayout()
#        self.back_button = QPushButton()
#        self.back_button.setIcon(QIcon("backmenu.png"))
#        self.back_button.setIconSize(QSize(250, 250))
#        self.back_button.setFlat(True)
#        self.back_button.clicked.connect(self.back_to_menu)
#
#        self.buttons.append(self.back_button)
#        self.button_icons[self.back_button] = {
#            "normal": QIcon("backmenu.png"),
#            "highlight": QIcon("highlight_backmenu_button.png")
#        }
#
#        top_row = QHBoxLayout()
#        top_row.addWidget(self.back_button)
#        top_row.addStretch()
#        layout.addLayout(top_row)
#
#        self.setLayout(layout)
#        self.highlight_selected()
#
#    
#    def back_to_menu(self):
#        from motor_roam_control import stop_motor_roam_control
#        stop_motor_roam_control() 
#        input_manager.start(self.stacked_widget.currentWidget().handle_direction)
#        self.stacked_widget.setCurrentIndex(0)
#        self.stacked_widget.currentWidget().activate_controller()
#        
#
#    def set_background(self, image_path):
#        self.setAutoFillBackground(True)
#        background = QPixmap(image_path)
#        palette = QPalette()
#        palette.setBrush(QPalette.Window, QBrush(background))
#        self.setPalette(palette)
#
#
#
#    def handle_direction(self, direction):
#        if direction == "Left" or direction == "Right":
#            self.selected_index = 0
#        elif direction == "Centre":
#            self.back_button.click()
#        self.highlight_selected()
#
#    def highlight_selected(self):
#        icon_type = "highlight" if self.selected_index == 0 else "normal"
#        self.back_button.setIcon(self.button_icons[self.back_button][icon_type])
#
#    def keyPressEvent(self, event):
#        key = event.key()
#        if key == Qt.Key_Left or key == Qt.Key_Right:
#            self.handle_direction("Left")
#        elif key == Qt.Key_Space:
#            self.handle_direction("Centre")
#
#    def activate_controller(self):
#        from motor_roam_control import start_motor_roam_control
#        input_manager.stop()  
#        start_motor_roam_control() 
#        print("[INFO] Motor Roam activated, controller input started.")
#        #button 7 or 10 back to main menu

if __name__ == '__main__':
    qRgb = queue.Queue()
    input_manager.qRgb = qRgb 
    input_manager.set_input_type("controller")
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()

    menu = MainMenu(stacked_widget)
    game = TicTacToe(stacked_widget)
    message_widget = MessageWidget(stacked_widget)
    free_roam = FreeRoamWidget(stacked_widget)
    #motor_roam = MotorRoamWidget(stacked_widget)
    
    stacked_widget.addWidget(menu)
    stacked_widget.addWidget(game)
    stacked_widget.addWidget(message_widget)
    stacked_widget.addWidget(free_roam)
    #stacked_widget.addWidget(motor_roam)

    menu.set_game_widget(game)
    menu.set_message_widget(message_widget)
    menu.set_free_roam_widget(free_roam)
    #menu.set_motor_roam_widget(motor_roam)

    stacked_widget.setCurrentWidget(menu)
    stacked_widget.showFullScreen()

    sys.exit(app.exec_())
