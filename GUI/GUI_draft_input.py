import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                             QHBoxLayout, QLabel, QMessageBox, QSpacerItem,
                             QSizePolicy, QStackedWidget)
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QIcon
from PyQt5.QtCore import Qt, QSize, QTimer, QMetaObject, Q_ARG
from control_modes_basic import controller_manager
import threading
from input_manager import input_manager
#from head_tracker import HeadTracker
#from input_manager import input_manager

class MainMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.game_widget = None
        self.message_widget = None
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
    def set_message_widget(self, message_widget):
        self.message_widget = message_widget
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
        self.stacked_widget.currentWidget().activate_controller()
    def __init__(self, stacked_widget):
        super().__init__()
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
            self.highlight_selected()
            if self.check_winner('X'):
                QTimer.singleShot(0, lambda: QMessageBox.information(self, "Game Over", "You win!"))
                self.reset_game()
                return
            QTimer.singleShot(0, self.delayed_computer_move)


    def delayed_computer_move(self):
        QTimer.singleShot(500, self.computer_move)
    
    def activate_controller(self):
        self.setFocus()
        input_manager.start(self.handle_direction)
    def computer_move(self):
        for idx in range(9):
            if self.board[idx] == '':
                self.board[idx] = 'O'
                self.highlight_selected()
                if self.check_winner('O'):
                    QTimer.singleShot(0, lambda: QMessageBox.information(self, "Game Over", "Computer wins!"))
                    self.reset_game()
                return


    def check_winner(self, player):
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        return any(self.board[a]==player and self.board[b]==player and self.board[c]==player for a,b,c in wins)

    def reset_game(self):
        self.board = [''] * 9
        self.selected_index = 0
        self.highlight_selected()

class Messages(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.setFocusPolicy(Qt.StrongFocus)
        self.stacked_widget = stacked_widget
        self.setWindowTitle("Tic-Tac-Toe")
        self.setGeometry(0, 0, 1920, 1080)
        self.set_background("message_background.png")
        self.turn = 'X'
        self.board = [''] * 9
        self.buttons = []
        self.selected_index = 0

        main_layout = QVBoxLayout()
        top_spacer = QSpacerItem(20, self.height() // 3, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addSpacerItem(top_spacer)
        
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
                self.buttons.append(btn)
                row_layout.addWidget(btn)
            main_layout.addLayout(row_layout)
        self.setLayout(main_layout)
    
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
    def set_background(self, image_path):
        self.setAutoFillBackground(True)
        background = QPixmap(image_path)
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(background))
        self.setPalette(palette)
    def activate_controller(self):
        from control_modes_basic import controller_manager
        input_manager.start(self.handle_direction)
    def activate_controller(self):
        self.setFocus()
        input_manager.start(self.handle_direction)
    def handle_direction(self, direction):
        if direction == "Left":
            self.selected_index = (self.selected_index - 1) % 9
        elif direction == "Right":
            self.selected_index = (self.selected_index + 1) % 9
        elif direction == "Centre":
            self.make_move(self.selected_index)

        self.highlight_selected()
    def highlight_selected(self):
        for i, btn in enumerate(self.buttons):
            cell_value = self.board[i]  # '', 'X', or 'O'
            icon_type = "highlight" if i == self.selected_index else "normal"
            btn.setIcon(self.button_icons[cell_value][icon_type])
          
    
if __name__ == '__main__':
    input_manager.set_input_type("controller")
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()

    menu = MainMenu(stacked_widget)
    game = TicTacToe(stacked_widget)
    message = Messages(stacked_widget)

    stacked_widget.addWidget(menu)
    stacked_widget.addWidget(game)
    stacked_widget.addWidget(message)
    menu.set_game_widget(game)
    menu.set_message_widget(message)

    stacked_widget.setCurrentWidget(menu)
    stacked_widget.showFullScreen()

    sys.exit(app.exec_())
