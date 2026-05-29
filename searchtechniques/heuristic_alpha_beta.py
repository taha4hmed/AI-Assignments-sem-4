def heuristic(state):
    score = 0
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for combo in winning_combinations:
        line = [state.board[i] for i in combo]
        if line.count('X') == 2 and line.count(' ') == 1:
            score += 10
        elif line.count('O') == 2 and line.count(' ') == 1:
            score -= 10
        elif line.count('X') == 1 and line.count(' ') == 2:
            score += 1
        elif line.count('O') == 1 and line.count(' ') == 2:
            score -= 1
    return score

def heuristic_alpha_beta(state, depth, alpha, beta, is_maximizing, max_depth):
    terminal, utility = state.is_terminal()
    if terminal:
        return utility, None
    
    if depth == max_depth:
        return heuristic(state), None

    best_move = None
    if is_maximizing:
        best_score = -float('inf')
        for move in state.get_legal_moves():
            new_state = state.make_move(move)
            score, _ = heuristic_alpha_beta(new_state, depth + 1, alpha, beta, False, max_depth)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score, best_move
    else:
        best_score = float('inf')
        for move in state.get_legal_moves():
            new_state = state.make_move(move)
            score, _ = heuristic_alpha_beta(new_state, depth + 1, alpha, beta, True, max_depth)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move
