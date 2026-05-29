from game import TicTacToe
from minimax import minimax
from alpha_beta import alpha_beta
from heuristic_alpha_beta import heuristic_alpha_beta
from mcts import mcts

def print_board(state):
    for i in range(0, 9, 3):
        print(f" {state.board[i]} | {state.board[i+1]} | {state.board[i+2]} ")
        if i < 6:
            print("-----------")
    print()

def main():
    print("Testing Minimax...")
    state = TicTacToe()
    state = state.make_move(4)
    state = state.make_move(0)
    print_board(state)
    score, move = minimax(state, True)
    print(f"Minimax optimal move for X: {move} with score {score}\n")

    print("Testing Alpha-Beta...")
    state = TicTacToe()
    state = state.make_move(4)
    state = state.make_move(0)
    score, move = alpha_beta(state, 0, -float('inf'), float('inf'), True)
    print(f"Alpha-Beta optimal move for X: {move} with score {score}\n")

    print("Testing Heuristic Alpha-Beta...")
    state = TicTacToe()
    state = state.make_move(4)
    state = state.make_move(0)
    score, move = heuristic_alpha_beta(state, 0, -float('inf'), float('inf'), True, 2)
    print(f"Heuristic Alpha-Beta move for X (depth 2): {move} with score {score}\n")

    print("Testing MCTS...")
    state = TicTacToe()
    state = state.make_move(4)
    state = state.make_move(0)
    move = mcts(state, 1000)
    print(f"MCTS suggested move for X (1000 iterations): {move}\n")

if __name__ == "__main__":
    main()
