from PyQt5.QtWidgets import (
    QApplication, QPushButton, QMainWindow, QCheckBox, QWidget, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QMenuBar, QGroupBox, QLabel, QSizePolicy, QLayout, QMessageBox,
    QSpinBox, QStackedWidget, QLineEdit
    )
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal 
from Model import Table, BlackjackTable, IPlayable
import time
import os


class GameWindow(QWidget):
    hit_signal = pyqtSignal()
    stand_signal = pyqtSignal()
    restart_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        self.setWindowTitle("Blackjack")
        self.setGeometry(100, 100, 1000, 1000)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.dealer_and_scores_layout = QHBoxLayout()
        self.players_container = QVBoxLayout()
        self.activity_layout = QHBoxLayout() # displays players moves (hit/stand) and round results (win/busted) vs dealer
        self.buttons_layout = QHBoxLayout()

        self.main_layout.addLayout(self.dealer_and_scores_layout)
        self.main_layout.addLayout(self.players_container)
        self.main_layout.addLayout(self.activity_layout)
        self.main_layout.addLayout(self.buttons_layout)

        self.dealer_layout = QVBoxLayout()
        self.dealer_layout.addWidget(QLabel("Dealer cards: "))
        self.dealer_cards_layout = QHBoxLayout()
        self.dealer_layout.addLayout(self.dealer_cards_layout)
        
        self.total_points_layout = QVBoxLayout()
        self.total_points_box = QGroupBox("Leaderboard")
        self.total_points_box.setLayout(self.total_points_layout)

        # addStretch to position the layout
        self.dealer_and_scores_layout.addStretch()
        self.dealer_and_scores_layout.addLayout(self.dealer_layout)
        self.dealer_and_scores_layout.addStretch()
        self.dealer_and_scores_layout.addWidget(self.total_points_box)

        # grid for player cards boxes
        self.players_cards_layout = QGridLayout()
        self.players_container.addWidget(QLabel("Players cards: "))
        self.players_container.addLayout(self.players_cards_layout)

        self.hit_button = QPushButton("HIT")
        self.stand_button = QPushButton("STAND")
        self.restart_button = QPushButton("RESTART")
        self.round_counter = QLabel("Round: 1")
        
        self.buttons_layout.addStretch()
        self.buttons_layout.addWidget(self.hit_button)
        self.buttons_layout.addWidget(self.stand_button)
        self.buttons_layout.addWidget(self.restart_button)
        self.buttons_layout.addWidget(self.round_counter)
        self.buttons_layout.addStretch()

        self.hit_button.clicked.connect(self.hit_signal.emit)
        self.stand_button.clicked.connect(self.stand_signal.emit)
        self.restart_button.clicked.connect(self.restart_signal.emit)
        
        # for fast and easy getting each player scores (not usefull here)
        self.players_scores = {}

    def init_setup(self, table: Table) -> None:
        ''' Initialize start window'''
        self.clear_layout(self.players_cards_layout)
        self.clear_layout(self.dealer_cards_layout)
        self.clear_layout(self.total_points_layout)
        self.clear_layout(self.activity_layout)

        self.round_counter.setText(f"Round: {table.round}")
        # hit/stand action labels
        self.player_turn = QLabel("")
        self.player_move = QLabel("")
        self.activity_layout.addWidget(self.player_turn)
        self.activity_layout.addWidget(self.player_move)
        # update leaderboard after every round
        self.update_leaderboard(table.players)
        
    def update_view(self, table: Table, action: str=None) -> None:
        self.clear_layout(self.dealer_cards_layout)
        # DEALER LAYOUT
        dealer = table.croupier
        dealer_value = dealer.get_hand_score() if table.is_game_over else "?"
        dealer_hand = dealer.hand if table.is_game_over else [dealer.hand[0], "X"] 
        d_box = QGroupBox()
       
        d_v_layout = QVBoxLayout()
        d_box.setLayout(d_v_layout)
        dealer_cards = QHBoxLayout()
        dealer_curr_val = QLabel()

        for i, card in enumerate(dealer_hand):
            if not table.is_game_over and i == 1:
                color = "red" if not isinstance(card, str) and card.suit in ['♦', '♥'] else "black"
                label = QLabel("X")
                label.setStyleSheet(f"border: 2px solid black; padding: 10px; background: white; color: {color};")
                label.setFixedSize(100, 145)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                font = QFont("Arial")
                font.setPointSize(100)
                label.setFont(font)
            else:
                label = CardWidget(card.rank[0], card.suit)
                #label = QLabel(f"{card.rank[0]}{card.suit}")
            #label.setStyleSheet(f"border: 2px solid black; padding: 10px; background: white; color: {color}; min-width: 60px; min-height: 100px;")
            dealer_cards.addWidget(label)

        self.dealer_cards_layout.addWidget(d_box)
        dealer_curr_val.setText(f"Hand value: {dealer_value}")
        d_v_layout.addLayout(dealer_cards)
        d_v_layout.addWidget(dealer_curr_val)

        # PLAYERS LAYOUT
        self.players_box = []
        # this 'if' reduces updating the players layout after all players have finished, but it causes
        # that the very last drawn card doesnt appear in the last player box (is_game_over condition 
        # too soon -> no idea how to get around this, so its turned off)
        #if not table.is_game_over: 
        self.clear_layout(self.players_cards_layout)
        max_players_horizontally = 3
        row = col = 0
        for i, player in enumerate(table.players):
            is_curr_player = i == table.curr_player_idx                         
            player_value = player.get_hand_score()

            p_box = QGroupBox(player.name)
            p_box.setStyleSheet(f"""
                    QGroupBox {{
                        border: 2px solid {'green' if is_curr_player else 'black'};
                        background-color: {'#eaffea' if is_curr_player else 'white'};
                        margin-top: 1.5em;
                    }}
                    QGroupBox::title {{
                        subcontrol-origin: margin;
                        subcontrol-position: top left;
                        padding: 0 3px;
                        background-color: none;
                    }}
                """)
            p_v_layout = QVBoxLayout()
            p_box.setLayout(p_v_layout)

            self.players_cards_layout.addWidget(p_box, row, col)
            col += 1
            if col >= max_players_horizontally:
                row += 1
                col = 0

            cards_layout = QGridLayout()
            max_cards_horizontally = 3
            for j, card in enumerate(player.hand):
                #color = "red" if card.suit in ['♦', '♥'] else "black"
                #label = QLabel(f"{card.rank[0]}{card.suit}")
                #label.setStyleSheet(f"border: 2px solid black; padding: 10px; background: white; color: {color}; min-width: 60px; min-height: 100px;")
                label = CardWidget(card.rank[0], card.suit)
                cards_layout.addWidget(label, 
                                        j // max_cards_horizontally,
                                        j % max_cards_horizontally)

            round_score_label = QLabel(f"Hand score: {player_value}")
            # 'reset' stylesheet since it automatically inherits styles from p_box (green border)
            round_score_label.setStyleSheet("border: none; background: none; color: black")
            
            p_v_layout.addLayout(cards_layout)
            p_v_layout.addWidget(round_score_label)
            self.players_box.append({
                'group_box': p_box,
                'cards_layout': cards_layout,
                'round_score_label': round_score_label 
                })
        if not table.is_game_over:
            self.show_player_move(table.get_curr_player(), action)
        
    def update_leaderboard(self, players: list) -> None:
        self.clear_layout(self.total_points_layout)
        for player in players:
            label = QLabel(f"{player.name}: {player.points}")
            self.total_points_layout.addWidget(label)
            self.players_scores[player.name] = label

    def clear_layout(self, layout: QLayout) -> None:
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                child_layout = item.layout()
                if widget:
                    widget.setParent(None)
                    widget.deleteLater()
                elif child_layout:
                    self.clear_layout(child_layout)

    def show_player_move(self, player: IPlayable, action: str | None):
        ''' Show player's action (hit/stand button click) '''
        self.player_turn.setText(f"{player.name} turn:")
        self.player_move.setFont(QFont("Helvetica", 14, 10, True))
        if action is not None:
            self.player_move.setText(f"{action.upper()}!")

    def show_results(self, dealer_score: int, res_table: list): 
        # note: res_table = [(player_name, hand_score, action)]
        ''' Show results of each player at the end of the round '''
        self.clear_layout(self.activity_layout)

        res_box = QVBoxLayout()
        res_box.addWidget(QLabel(f"Dealer score: {dealer_score}"))
        for res in res_table:
            res_box.addWidget(QLabel(f"{res[0]} : {res[1]} -> {res[2].upper()}!"))
        self.activity_layout.addStretch()    
        self.activity_layout.addLayout(res_box)
        self.activity_layout.addStretch()
        
    def no_cards_warn(self):
        ''' Out of cards warning window '''
        msg = QMessageBox()
        msg.setText("No more cards in the deck!")
        self.disable_game_buttons(self)
        msg.exec()

    def disable_game_buttons(self):    
        self.hit_button.setDisabled(True)
        self.stand_button.setDisabled(True)
    
    def enable_game_buttons(self):    
        self.hit_button.setEnabled(True)
        self.stand_button.setEnabled(True)
    

class StartWindow(QWidget):
    show_setup_dial_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.welcome = QLabel("WELCOME TO BLACKJACK GAME")
        self.setup_button = QPushButton("Choose players")

        self.main_layout.addStretch()
        self.main_layout.addWidget(self.welcome, alignment=Qt.AlignmentFlag.AlignHCenter)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.setup_button)

        self.setup_button.clicked.connect(self.show_setup_dial_signal.emit)

        
class SetupDialog(QWidget):
    # any args can be passed to the signal
    accept_names_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # "bar" with numbers to choose
        self.spin_box = QSpinBox()
        self.spin_box.setRange(1, 6)

        self.input_layout = QVBoxLayout()

        self.label = QLabel("Enter number of players: ")
        self.start_button = QPushButton("Accept")

        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.spin_box)
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.start_button)
        # action to change the number in the bar
        self.spin_box.valueChanged.connect(self.update_players_input)
        self.start_button.clicked.connect(self.save_player_names)
        
        self.players_input = [] # to store names from the input      
        self.update_players_input() # init window for the first time

    def update_players_input(self):
        ''' Update view as player count changes '''
        for input in self.players_input:
            input.deleteLater()
        
        self.players_input = []

        for i in range(self.spin_box.value()):
            line = QLineEdit()
            line.setPlaceholderText(f"Enter {i+1} player name...")
            self.input_layout.addWidget(line)
            self.players_input.append(line)

    def save_player_names(self):
        inputs = [pl.text() or f"Player {i}" for i, pl in enumerate(self.players_input, 1)]
        self.accept_names_signal.emit(inputs)


class CardWidget(QWidget):
    ''' Card view loaded from a file '''
    def __init__(self, rank, suit, cards_dir='cards_png'):
        super().__init__()
        self.rank = rank
        self.suit = suit
        self.cards_dir = cards_dir
        self.init_card()

    def generate_card_endpoint(self):
        mapper = {'♣': 'C', '♦': 'D', '♥': 'H', '♠': 'S'}
        return f"{self.rank}{mapper[self.suit]}.png" 
    
    def init_card(self):
        # /cards_png/rank+suit.png 
        path = os.path.join(self.cards_dir, self.generate_card_endpoint())
        print("path", path)
        self.card_layout = QVBoxLayout()
        self.setLayout(self.card_layout)
        self.label = QLabel()
        self.card_layout.addWidget(self.label)

        if os.path.exists(path):
            pixmap = QPixmap(path).scaled(100, 145, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.label.setPixmap(pixmap)
        else: # if there is no such file
            color = "red" if self.suit in ['♦', '♥'] else "black"
            self.label.setText(f"{self.rank}{self.suit}")
            self.label.setStyleSheet(f"border: 2px solid black; padding: 10px; background: white; color: {color}; min-width: 60px; min-height: 100px;")
