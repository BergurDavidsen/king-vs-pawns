from flask import Flask, redirect, render_template, jsonify, request, session, url_for
from flask_socketio import SocketIO, emit, join_room
import os
import secrets

from game.board import Board
from game.game_analysis import analyze_game, normalize_moves
from game.players.minimax_player import MinimaxPlayer


app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

board = Board()
ai = MinimaxPlayer("AI")

# --- Online PvP (per-room boards, separate from HTTP session board) ---
# room_code -> {"board": Board, "king_sid": str | None, "pawn_sid": str | None}
online_games: dict[str, dict] = {}
sid_to_room: dict[str, str] = {}


def _new_room_code() -> str:
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(secrets.choice(alphabet) for _ in range(6))


def state_for_player(
    b: Board, your_side: int, *, waiting_for_opponent: bool = False, history:list
) -> dict:
    moves = b.get_legal_moves()
    winner = b.is_terminal(moves)
    return {
        "fen": b.to_fen(),
        "turn": b.turn,
        "winner": winner,
        "human_side": your_side,
        "waiting_for_opponent": waiting_for_opponent,
        "online": True,
        "history": history if history is not None else []
    }


def broadcast_online_state(room_code: str) -> None:
    g = online_games.get(room_code)
    if not g:
        return
    b = g["board"]
    history = g.get("ply_log", [])
    king_sid = g.get("king_sid")
    pawn_sid = g.get("pawn_sid")
    waiting = pawn_sid is None
    if king_sid:
        socketio.emit(
            "online_state",
            state_for_player(b, Board.KING, waiting_for_opponent=waiting, history=history),
            room=king_sid,
        )
    if pawn_sid:
        socketio.emit(
            "online_state",
            state_for_player(b, Board.PAWN, waiting_for_opponent=False, history=history),
            room=pawn_sid,
        )


def leave_online_room(sid: str) -> None:
    room = sid_to_room.pop(sid, None)
    if not room:
        return
    g = online_games.get(room)
    if not g:
        return
    king = g.get("king_sid")
    pawn = g.get("pawn_sid")
    if king == sid:
        online_games.pop(room, None)
        if pawn:
            sid_to_room.pop(pawn, None)
            socketio.emit("online_peer_left", {}, room=pawn)
    elif pawn == sid:
        g["pawn_sid"] = None
        nb = Board()
        nb.reset_board()
        g["board"] = nb
        if king:
            socketio.emit("online_peer_left", {}, room=king)
            socketio.emit(
                "online_state",
                state_for_player(nb, Board.KING, waiting_for_opponent=True, history=[]),
                room=king,
            )


def format_evaluation(val):
    if val >= 90:
        return f"Mate in {100 - val}"
    elif val <= -90:
        return f"Mate in {-(100 + val)}"
    else:
        return str(val)


@app.route("/")
def index():
    return redirect(url_for("analysis_page"))


@app.route("/analysis")
def analysis_page():
    board.reset_board()
    session.pop("ply_log", None)
    return render_template("analysis.html")


@app.route("/online")
def online_play():
    return render_template("online.html")

@app.route("/rules")
def rules():
    return render_template("rules.html")

@app.route("/select_side", methods=["POST"])
def select_side():
    data = request.json
    side = data.get("side")  # 2, 1, or 'pvp'
    board.reset_board()
    session["ply_log"] = []

    if side == "pvp":
        session["human_side"] = "pvp"
    else:
        session["human_side"] = int(side)
        # If human plays Pawns, AI (King) moves first
        if session["human_side"] == board.PAWN:
            ai_move = ai.get_best_move(board)
            if ai_move:
                board.move_piece(*ai_move)
                session["ply_log"] = session["ply_log"] + [
                    {"from": list(ai_move[0]), "to": list(ai_move[1])}
                ]

    return get_state()


@app.route("/legal_moves", methods=["POST"])
def legal_moves():
    data = request.json
    x, y = data["pos"]

    moves = board.get_legal_moves()

    legal = [m for m in moves if m[0] == (x, y)]

    return jsonify({"moves": [m[1] for m in legal]})


@app.route("/evaluate", methods=["GET"])
def evaluate():
    value = ai.minimax(board)
    best_move = ai.get_best_move(board)
    lines = ai.get_top_lines(board, depth_limit=4)

    return jsonify(
        {
            "evaluation": value,
            "eval_text": format_evaluation(value),
            "best_move": best_move,
            "lines": lines,
        }
    )


@app.route("/move", methods=["POST"])
def move():
    if "human_side" not in session:
        return jsonify({"error": "Select a side first"}), 400

    data = request.json
    from_pos = tuple(data["from"])
    to_pos = tuple(data["to"])
    is_pvp = session.get("human_side") == "pvp"

    # In PvP, any side can move. In Solo, check turn.
    if not is_pvp and board.turn != session["human_side"]:
        return get_state()

    # Execute Move
    if board.move_piece(from_pos, to_pos):
        log = list(session.get("ply_log", []))
        log.append({"from": list(from_pos), "to": list(to_pos)})
        session["ply_log"] = log
        res = board.is_terminal(board.get_legal_moves())
        # Only trigger AI if NOT in PvP mode and game isn't over
        if not is_pvp and res == 0:
            ai_move = ai.get_best_move(board)
            if ai_move:
                board.move_piece(*ai_move)
                log = list(session["ply_log"])
                log.append(
                    {"from": list(ai_move[0]), "to": list(ai_move[1])}
                )
                session["ply_log"] = log

    return get_state()


@app.route("/state", methods=["GET"])
def get_state():
    moves = board.get_legal_moves()
    winner = board.is_terminal(moves)

    return jsonify(
        {
            "fen": board.to_fen(),
            "turn": board.turn,
            "winner": winner,
            "human_side": session.get("human_side"),
            "ply_log": session.get("ply_log", []),
        }
    )


@app.route("/undo", methods=["POST"])
def undo_move():
    board.undo()
    log = session.get("ply_log")
    if log:
        session["ply_log"] = log[:-1]

    return get_state()


@app.post("/game/load")
def game_load():
    data = request.get_json(silent=True) or {}
    raw = data.get("moves", [])
    try:
        moves = normalize_moves(raw)
    except (KeyError, TypeError, IndexError, ValueError):
        return jsonify({"error": "Invalid moves format (need from/to arrays)."}), 400

    board.reset_board()
    for m in moves:
        f, t = tuple(m["from"]), tuple(m["to"])
        if not board.move_piece(f, t):
            return jsonify({"error": "Illegal move in saved game."}), 400

    session["ply_log"] = moves
    session["human_side"] = "pvp"
    return get_state()


@app.get("/game/export")
def game_export():
    return jsonify(
        {
            "version": 1,
            "variant": "king-vs-pawn",
            "moves": session.get("ply_log", []),
        }
    )


@app.post("/game/analyze")
def game_analyze():
    data = request.get_json(silent=True) or {}
    raw = data.get("moves")
    if raw is None:
        raw = session.get("ply_log", [])
    try:
        moves = normalize_moves(raw)
    except (KeyError, TypeError, IndexError, ValueError):
        return jsonify({"error": "Invalid moves format."}), 400

    if not moves:
        return jsonify({"error": "No moves to analyze."}), 400

    try:
        steps = analyze_game(ai, moves)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify({"steps": steps})


@socketio.on("online_create")
def on_online_create():
    sid = request.sid
    leave_online_room(sid)
    code = _new_room_code()
    while code in online_games:
        code = _new_room_code()
    b = Board()
    b.reset_board()
    online_games[code] = {"board": b, "king_sid": sid, "pawn_sid": None, "ply_log": []}
    sid_to_room[sid] = code
    join_room(f"game_{code}")
    emit(
        "online_state",
        state_for_player(b, Board.KING, waiting_for_opponent=True, history=[]),
    )
    emit("online_room_code", {"room_code": code})


@socketio.on("online_join")
def on_online_join(data):
    sid = request.sid
    raw = (data or {}).get("room_code", "")
    code = raw.strip().upper().replace(" ", "")
    g = online_games.get(code)
    if not g or g["pawn_sid"] is not None:
        emit("online_error", {"message": "Invalid code or game is full."})
        return
    if g["king_sid"] == sid:
        emit("online_error", {"message": "You are already hosting this game."})
        return
    leave_online_room(sid)
    g = online_games.get(code)
    if not g or g["pawn_sid"] is not None:
        emit("online_error", {"message": "Room closed or became full — try again."})
        return
    g["pawn_sid"] = sid
    sid_to_room[sid] = code
    join_room(f"game_{code}")
    b = g["board"]
    emit("online_state", state_for_player(b, Board.PAWN, waiting_for_opponent=False, history=[]))
    socketio.emit(
        "online_state",
        state_for_player(b, Board.KING, waiting_for_opponent=False, history=[]),
        room=g["king_sid"],
    )


@socketio.on("online_move")
def on_online_move(data):
    sid = request.sid
    room = sid_to_room.get(sid)
    if not room:
        emit("online_error", {"message": "Not in an online game."})
        return
    g = online_games.get(room)
    if not g:
        emit("online_error", {"message": "Game no longer exists."})
        return
    if g["pawn_sid"] is None:
        emit("online_error", {"message": "Waiting for opponent to join."})
        return
    if g["king_sid"] == sid:
        side = Board.KING
    elif g["pawn_sid"] == sid:
        side = Board.PAWN
    else:
        emit("online_error", {"message": "Not in an online game."})
        return
    b = g["board"]
    if b.turn != side:
        emit("online_error", {"message": "Not your turn."})
        return
    payload = data or {}
    from_pos = tuple(payload["from"])
    to_pos = tuple(payload["to"])
    
    if b.move_piece(from_pos, to_pos):
        g["ply_log"].append({"from": list(from_pos), "to": list(to_pos)})
        broadcast_online_state(room)
    else:
        emit("online_error", {"message": "Illegal move."})


@socketio.on("online_legal")
def on_online_legal(data):
    sid = request.sid
    room = sid_to_room.get(sid)
    if not room:
        return {"moves": []}
    g = online_games.get(room)
    if not g or g["pawn_sid"] is None:
        return {"moves": []}
    if g["king_sid"] == sid:
        side = Board.KING
    elif g["pawn_sid"] == sid:
        side = Board.PAWN
    else:
        return {"moves": []}
    payload = data or {}
    x, y = payload["pos"]
    b = g["board"]
    if b.turn != side:
        return {"moves": []}
    if b.get_piece(x, y) != side:
        return {"moves": []}
    moves = b.get_legal_moves()
    legal = [m[1] for m in moves if m[0] == (x, y)]
    return {"moves": legal}


@socketio.on("online_leave")
def on_online_leave():
    leave_online_room(request.sid)


@socketio.on("disconnect")
def on_disconnect():
    leave_online_room(request.sid)
    
@app.route("/game/sync_online", methods=["POST"])
def sync_online():
    """Transfer an online game log to the user's local session for analysis."""
    sid = request.sid # This requires a specific setup, usually you'd pass the room code
    data = request.json
    room_code = data.get("room_code")
    
    g = online_games.get(room_code)
    if g:
        session["ply_log"] = g["ply_log"]
        session["human_side"] = "pvp" # Set to pvp so engine doesn't auto-move
        return jsonify({"status": "synced"})
    return jsonify({"error": "Room not found"}), 404


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000, debug=False)
