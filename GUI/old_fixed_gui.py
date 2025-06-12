import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt5.QtCore import Qt

from input_manager import input_manager
from control_modes_basic import controller_manager
from GUI_draft_input_old import MainMenu, TicTacToe, MessageWidget, DiceWidget, FreeRoamWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Charis GUI")
        self.setGeometry(100, 100, 800, 600)

        self.stack = QStackedWidget(self)
        self.setCentralWidget(self.stack)

        self.main_menu = MainMenu(self.stack)
        self.tic_tac_toe = TicTacToe(self.stack)
        self.message_widget = MessageWidget(self.stack)
        self.free_roam_widget = FreeRoamWidget(self.stack)

        self.stack.addWidget(self.main_menu)
        self.stack.addWidget(self.tic_tac_toe)
        self.stack.addWidget(self.message_widget)
        self.stack.addWidget(self.free_roam_widget)

        self.main_menu.set_game_widget(self.tic_tac_toe)
        self.main_menu.set_message_widget(self.message_widget)
        self.main_menu.set_free_roam_widget(self.free_roam_widget)
        self.stack.setCurrentWidget(self.main_menu)

        try:
            self.main_menu.page_selected.connect(self.on_page_selected)
        except AttributeError:
            pass

    def on_page_selected(self, page_index):
        """Handler for page selection if MainMenu emits a signal."""
        self.stack.setCurrentIndex(page_index)
        if self.stack.currentWidget() is self.free_roam_widget:
            from draft_ps5_control_thread import start_ps5_control
            start_ps5_control()
        else:
            try:
                from draft_ps5_control_thread import stop_ps5_control
                stop_ps5_control()
            except ImportError:
                pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
