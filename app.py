from PyQt5.QtWidgets import QApplication, QPushButton, QMainWindow, QCheckBox, QWidget, QVBoxLayout, QHBoxLayout, QMenuBar
import sys
from View import GameWindow
from Model import BlackjackTable, Player, Croupier
from Controller import BlackjackController
from MainWindow import MainWindow



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # init and show main window
    window = MainWindow()
    window.show()

    app.exec()