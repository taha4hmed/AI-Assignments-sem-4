def alpha_beta(state, depth, alpha, beta, is_maximizing):
    terminal, utility = state.is_terminal()
    if terminal:
        return utility, None

    best_move = None
    if is_maximizing:
        best_score = -float('inf')
        for move in state.get_legal_moves():
            new_state = state.make_move(move)
            score, _ = alpha_beta(new_state, depth + 1, alpha, beta, False)
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
            score, _ = alpha_beta(new_state, depth + 1, alpha, beta, True)
            if score < best_score:
                best_score = score
                best_move = move
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score, best_move
