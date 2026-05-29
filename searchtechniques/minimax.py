def minimax(state, is_maximizing):
    terminal, utility = state.is_terminal()
    if terminal:
        return utility, None

    best_move = None
    if is_maximizing:
        best_score = -float('inf')
        for move in state.get_legal_moves():
            new_state = state.make_move(move)
            score, _ = minimax(new_state, False)
            if score > best_score:
                best_score = score
                best_move = move
        return best_score, best_move
    else:
        best_score = float('inf')
        for move in state.get_legal_moves():
            new_state = state.make_move(move)
            score, _ = minimax(new_state, True)
            if score < best_score:
                best_score = score
                best_move = move
        return best_score, best_move
