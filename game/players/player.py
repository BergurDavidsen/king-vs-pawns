from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, player_name):
        self.name = player_name
        
    @abstractmethod
    def get_best_move(self, board):
        pass