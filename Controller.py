import sys, time
import random
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
import Model, View
from Model import Table, BlackjackTable, IPlayable, Player, Croupier
from View import GameWindow

class BlackjackController:
    ''' Controller acts as a bridge between Model and View '''
    def __init__(self, table: Table, view: GameWindow):
        self.table = table
        self.view = view
        # show dealer's cards drawn one by one with 0,5s break
        self.timer = QTimer()
        self.timer.setInterval(500) # ms
        self.timer.timeout.connect(self.dealer_hit_step) # this is called every 500 ms
        # 'connect' buttons signals with particular functions
        self.view.hit_signal.connect(self.hit)
        self.view.stand_signal.connect(self.stand)
        self.view.restart_signal.connect(self.restart)
        self.view.show()
        # start the game
        self.restart()

    def hit(self):
        if self.table.is_game_over:
            return
        player = self.table.get_curr_player()
        try:
            player.hit()
        
        except IndexError: # if no more cards in the deck
            self.view.no_cards_warn()
            return
    
        if player.get_hand_score() > 21:
            self.table.next_player() # if no more players -> it sets is_game_over=True
            self.update_view('busted')
            if self.table.is_game_over:
                self.view.disable_game_buttons()
                self.dealer_turn()
        else:
            self.update_view('hit')

    def stand(self):
        if self.table.is_game_over:
            return
        self.table.next_player() # if no more players -> it sets is_game_over=True
        self.update_view('stand')
        if self.table.is_game_over:
            self.view.disable_game_buttons()
            self.dealer_turn()


    def restart(self):
        self.table.start_game()
        self.view.init_setup(self.table)
        self.update_view()
        self.view.enable_game_buttons()

    def get_results(self):
        results = []
        dealer_score = self.table.croupier.get_hand_score()
        for player in self.table.players:
            message = 'win'
            player_score = player.get_hand_score()
            if dealer_score <= 21:
                if player_score > 21:
                    message = 'busted'
                elif player_score > dealer_score:
                    message = 'win'
                    player.points += 1
                else:
                    message = 'busted'
            # if dealer's score > 21, all remaining players win, so we skip checking
            else:
                player.points += 1
            results.append((player.name, player_score, message))
        return results

    def update_view(self, action: str=None):
        self.view.update_view(self.table, action)

    def dealer_turn(self):
        # for eventual counting how many cards are taken or to implement custom logic or animating each card with counting
        self.dealer_hit_index = 0   
        self.dealer = self.table.croupier
        self.timer.start() # trigger to start executing dealer_hit_step
    
    def dealer_hit_step(self):
        try:
            self.dealer.hit()
            self.update_view()
        except IndexError:
            self.view.no_cards_warn()
            return
        
        if self.dealer.get_hand_score() > 17:
            self.dealer_finish_step()

    def dealer_finish_step(self):
        '''Calculate the results of each player and print them'''
        self.timer.stop()
        results = self.get_results()
        self.view.show_results(self.dealer.get_hand_score(), results)

        