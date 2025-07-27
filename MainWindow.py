from PyQt5.QtWidgets import (
    QApplication, QPushButton, QMainWindow, QCheckBox, QWidget, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QMenuBar, QGroupBox, QLabel, QSizePolicy, QLayout, QMessageBox,
    QSpinBox, QStackedWidget, QLineEdit
    )
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from Model import Table, BlackjackTable, Player, Croupier
from Controller import BlackjackController
from View import GameWindow, SetupDialog, StartWindow
import time


class MainWindow(QMainWindow):
    ''' This is the main window for all views - it remains the same, but the views displayed in it change '''
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Blackjack")
        self.setGeometry(100, 100, 500, 400)
        # add all views on the stack
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        self.start_window = StartWindow()
        self.setup_window = SetupDialog()

        # add individual windows on the stack
        self.stack.addWidget(self.start_window)
        self.stack.addWidget(self.setup_window)

        # when someone clicks button in the start_window -> signal it -> and here, connect that signal with the the SLOT (function)
        self.start_window.show_setup_dial_signal.connect(self.show_setup_dial)
        self.setup_window.accept_names_signal.connect(self.start_game)
        # render choosen window
        self.stack.setCurrentWidget(self.start_window)

    def show_setup_dial(self):
        ''' Show players setup window '''
        self.stack.setCurrentWidget(self.setup_window)

    def start_game(self, players_list: list):
        ''' Finalize game setup '''
        self.game_window = GameWindow()
        self.table = BlackjackTable("Blackjack", max_players=10)
        self.table.add_croupier(Croupier("Dealer"))

        # player_lists fetched from the SetupDialog in form of list of strings
        for player in players_list:
            self.table.add_player(Player(player))

        self.stack.addWidget(self.game_window)
        self.stack.setCurrentWidget(self.game_window)

        self.controller = BlackjackController(self.table, self.game_window)
