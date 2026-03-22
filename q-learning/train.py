import sys
import time
import os
from agent_player import QLearningAgent
from board import Board
from minimax_player import MinimaxPlayer

def print_progress_bar(iteration, total, length=40):
    percent = iteration / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {percent*100:.2f}% ({iteration}/{total})')
    sys.stdout.flush()

def main():
    # --- Configuration ---
    training_games = 500000 
    steps = 50
    update_every = max(1, training_games // steps)
    
    # Initialize the Agent
    q_agent = QLearningAgent("Q_Bot")
    
    # Optional: Load existing table to continue training
    if os.path.exists("chess_variant_qtable.json"):
        q_agent.set_q_table("chess_variant_qtable.json")
        print("Continuing training from existing Q-table...")

    # The Teacher: Minimax will force the Q-Agent to learn "real" moves
    teacher = MinimaxPlayer("Teacher")
    
    win_counts = {"Q_Bot": 0, "Teacher": 0}
    board = Board()

    print(f"Training Q-Agent (King) against Minimax (Pawns) for {training_games} games...")
    start_time = time.time()

    for i in range(training_games):
        board.reset_board()
        
        while True:
            # 1. Check for game over
            moves = board.get_legal_moves()
            result = board.is_terminal(moves)
            
            if result != 0:
                # 2. Update Q-values using your new reverse-propagation logic
                # result is 100 (King Win) or -100 (Pawn Win)
                q_agent.update_q_values(result)
                
                if result == 100:
                    win_counts["Teacher"] += 1
                else:
                    win_counts["Q_Bot"] += 1
                break
            
            # 3. Choose Move
            if board.turn == board.KING:
                # Q-Agent learns as the King
                move = teacher.get_best_move(board)
            else:
                # Teacher plays optimally as the Pawns
                move = q_agent.get_best_move(board)
            
            # 4. Execute Move
            board.move_piece(*move)
        
        # Epsilon Decay: Reduce randomness over time
        q_agent.epsilon = max(0.05, q_agent.epsilon * 0.999)

        if i % update_every == 0:
            print_progress_bar(i, training_games)

    print_progress_bar(training_games, training_games)
    print(f"\nTraining took {round(time.time() - start_time, 2)}s")
    
    # Save the knowledge
    q_agent.store_q_values("chess_variant_qtable.json")
    
    print(f"Stats: Q-Bot Wins: {win_counts['Q_Bot']} | Teacher Wins: {win_counts['Teacher']}")

if __name__ == "__main__":
    main()