"""Full-game analysis: compare each played move to engine-best (minimax + memo)."""

from __future__ import annotations

from game.board import Board


def format_eval(val: float) -> str:
    if val >= 90:
        return f"Mate in {100 - int(val)}"
    if val <= -90:
        return f"Mate in {-(100 + int(val))}"
    return str(int(val))


def _eval_after(board: Board, ai, move: tuple[tuple[int, int], tuple[int, int]]) -> float:
    b = board.copy()
    if not b.move_piece(move[0], move[1]):
        raise ValueError("illegal move in _eval_after")
    return float(ai.minimax(b))


def _best_value_and_moves(board: Board, ai) -> tuple[float, list[tuple]]:
    moves = board.get_legal_moves()
    if not moves:
        return 0.0, []
    scored: list[tuple[float, tuple]] = []
    for m in moves:
        v = _eval_after(board, ai, m)
        scored.append((v, m))
    if board.turn == Board.KING:
        v_best = max(v for v, _ in scored)
    else:
        v_best = min(v for v, _ in scored)
    best_moves = [m for v, m in scored if v == v_best]
    return float(v_best), best_moves


def classify_ply(board: Board, ai, played: tuple[tuple[int, int], tuple[int, int]]) -> dict:
    moves = board.get_legal_moves()
    eval_before = float(ai.minimax(board))
    if not moves:
        return {
            "eval_before": eval_before,
            "eval_before_text": format_eval(eval_before),
            "terminal": True,
        }

    is_only = len(moves) == 1
    played_t = (tuple(played[0]), tuple(played[1]))
    v_played = _eval_after(board, ai, played_t)
    v_best, best_moves_eq = _best_value_and_moves(board, ai)
    engine_pick = ai.get_best_move(board)

    if board.turn == Board.KING:
        regret = v_best - v_played
    else:
        regret = v_played - v_best

    matches = any(
        played_t[0] == m[0] and played_t[1] == m[1] for m in best_moves_eq
    )

    if is_only:
        label = "forced"
    elif matches:
        label = "best"
    else:
        r = max(0.0, regret)
        if r <= 2:
            label = "good"
        elif r <= 12:
            label = "inaccuracy"
        elif r <= 35:
            label = "mistake"
        else:
            label = "blunder"

    bm_out = None
    if engine_pick:
        bm_out = {"from": list(engine_pick[0]), "to": list(engine_pick[1])}

    return {
        "terminal": False,
        "side": "king" if board.turn == Board.KING else "pawns",
        "eval_before": eval_before,
        "eval_before_text": format_eval(eval_before),
        "eval_after_played": v_played,
        "eval_after_played_text": format_eval(v_played),
        "eval_after_best": v_best,
        "eval_after_best_text": format_eval(v_best),
        "regret": regret,
        "best_move": bm_out,
        "classification": label,
        "is_only_move": is_only,
    }


def analyze_game(ai, moves: list) -> list[dict]:
    """Replay moves from the start position and annotate each ply."""
    b = Board()
    b.reset_board()
    out: list[dict] = []

    for i, raw in enumerate(moves):
        fr = tuple(raw["from"])
        to = tuple(raw["to"])
        played = (fr, to)
        fen_before = b.to_fen()
        info = classify_ply(b, ai, played)
        if info.get("terminal"):
            break
        if not b.move_piece(fr, to):
            raise ValueError(f"Illegal move at ply {i + 1}")
        fen_after = b.to_fen()
        moves_after = b.get_legal_moves()
        winner = b.is_terminal(moves_after)
        step = {
            "ply": i + 1,
            "fen_before": fen_before,
            "fen_after": fen_after,
            "played": {"from": list(fr), "to": list(to)},
            **{k: v for k, v in info.items() if k != "terminal"},
        }
        if winner != 0:
            step["game_over"] = True
            step["winner"] = winner
        out.append(step)
        if winner != 0:
            break

    return out


def normalize_moves(moves: list) -> list[dict]:
    norm: list[dict] = []
    for m in moves:
        norm.append(
            {
                "from": [int(m["from"][0]), int(m["from"][1])],
                "to": [int(m["to"][0]), int(m["to"][1])],
            }
        )
    return norm
