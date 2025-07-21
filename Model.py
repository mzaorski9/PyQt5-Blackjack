import sys
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from abc import ABC, abstractmethod

class Table(ABC):
    ...

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    
    def __str__(self):
        return f"{self.rank[0]}{self.suit}"


class Deck:
    ranks =  {'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 10, 'Q': 10, 'K': 10}
    suits = ['♣', '♦', '♥', '♠'] # clubs, diamonds, hearts, spades
    # note: color: red for '♦', '♥'
    #       color: black for '♣', '♠'
    def __init__(self):
        self.cards = [Card((rank, val), suit) for rank, val in self.ranks.items() for suit in self.suits]

    def __len__(self):
        return len(self.cards)
 
class IPlayable(ABC):
    def __init__(self, name: str):
        self.name = name
        self.hand = []
        self.hand_score = 0
        self.points = 0
        self.game_table = None 
    
    def assign_table(self, table: Table):
        if not self.game_table:
            self.game_table = table
        else:
            print("This player is already sitting at the gaming table")
    
    def get_hand_score(self):
        aces = sum(1 for card in self.hand if card.rank[0] == 'A')
        total = sum(card.rank[1] for card in self.hand)
        # since ace can be equal to 11 or 1, we decrease its value accordingly
        while aces and total > 21:
            total -= 10
            aces -= 1
        return total

    @abstractmethod
    def hit(self):
        ...

   
class Table(ABC):
    def __init__(self, game_type: str, max_players: int):
        # self.game_type = game_type
        self.max_players = max_players
        self.croupier = None
        self.players = []
        self.deck = Deck()
        self.is_game_over = False
        self.round = 0
        self.curr_player_idx = 0
        
    def restart_game(self):
        if self.players and self.croupier:
            self.croupier.hand.clear()
            self.croupier.hand_score = 0
            for player in self.players:
                player.hand.clear()
                player.hand_score = 0
                player.has_passed = False
            self.deck = Deck()
            self.is_game_over = False
            self.curr_player_idx = 0
            self.shuffle()
        else:
            raise Exception("There is no complete set for the game!")

    def shuffle(self):
        random.shuffle(self.deck.cards)

    def get_curr_player(self):
        return self.players[self.curr_player_idx]
    
    def next_round(self):
        self.round += 1
    
    @abstractmethod
    def add_player(self, player: IPlayable):
        ...
    @abstractmethod
    def add_croupier(self, croupier: IPlayable):
        ...
    @abstractmethod
    def start_game(self):
        ...
    @abstractmethod
    def next_player(self):
        ...

    
class BlackjackTable(Table):
    def add_player(self, player: IPlayable):
        if len(self.players) < self.max_players:
            self.players.append(player)
            player.assign_table(self)
        else:
            print("The game has full set of players!")
    
    def add_croupier(self, croupier: IPlayable):
        if not self.croupier:
            self.croupier = croupier
            self.croupier.assign_table(self)
        else:
            print("The croupier is already in the game!")

    def start_game(self):
        ''' Start Blackjack game '''
        self.round += 1
        self.restart_game()
        if self.players and self.croupier:
            for _ in range(2):
                for player in self.players:
                    player.hit()
                self.croupier.hit()
        else:
            print("There is no complete set for the game!")
    
    def next_player(self) -> None:
        self.curr_player_idx += 1
        if self.curr_player_idx >= len(self.players):
            self.is_game_over = True

class Player(IPlayable):
    def hit(self):
        try:
            card = self.game_table.deck.cards.pop()
            self.hand.append(card)
        except IndexError:
            print("No more cards in the deck!")

class Croupier(IPlayable):
    def hit(self):
        try:
            # while self.hand_score <= 17:
                card = self.game_table.deck.cards.pop()
                self.hand.append(card)
        except IndexError:
            print("No more cards in the deck!")

