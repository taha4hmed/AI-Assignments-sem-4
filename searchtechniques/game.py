import copy

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_player = 'X'

    def get_legal_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def make_move(self, move):
        new_state = copy.deepcopy(self)
        new_state.board[move] = new_state.current_player
        new_state.current_player = 'O' if new_state.current_player == 'X' else 'X'
        return new_state

    def is_terminal(self):
        winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for combo in winning_combinations:
            if self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] != ' ':
                return True, 1 if self.board[combo[0]] == 'X' else -1
        if ' ' not in self.board:
            return True, 0
        return False, None
    
    def get_winner(self):
        term, val = self.is_terminal()
        if term:
            return val
        return None
