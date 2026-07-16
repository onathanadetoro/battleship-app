import streamlit as st
import random

# --- Game Initialization and State Management --- #
def initialize_game():
    st.session_state.game_phase = "player_place_ship" # Initial phase
    st.session_state.message = "Welcome to Battleship! Place your ship on the board below."
    st.session_state.board_size = 8

    # Player's board (where the computer guesses)
    st.session_state.player_board = [['~' for _ in range(st.session_state.board_size)] for _ in range(st.session_state.board_size)]
    st.session_state.player_ship_position = None # (row, col) for player's ship
    st.session_state.player_hits_by_computer = set()

    # Computer's board (where the player guesses)
    st.session_state.computer_board = [['~' for _ in range(st.session_state.board_size)] for _ in range(st.session_state.board_size)]
    st.session_state.computer_ship_positions = [] # List of (row, col) for computer's ships

    # Place computer's ships (2 ships)
    for _ in range(2):
        while True:
            ship_row = random.randint(0, st.session_state.board_size - 1)
            ship_col = random.randint(0, st.session_state.board_size - 1)
            if (ship_row, ship_col) not in st.session_state.computer_ship_positions:
                st.session_state.computer_ship_positions.append((ship_row, ship_col))
                break

    st.session_state.player_guesses = set() # Store player's past guesses on computer's board
    st.session_state.computer_guesses = set() # Store computer's past guesses on player's board
    st.session_state.player_sunk_computer_ships = 0
    st.session_state.computer_sunk_player_ships = 0 # Should be 0 or 1 for player's single ship
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.current_turn = 0
    st.session_state.max_turns = 20 # Can adjust as needed

# --- Display Board Function --- #
def display_board(board_data, click_handler=None, is_player_board=False):
    st.markdown(f"### {'Your Board' if is_player_board else 'Computer\'s Board'}")
    for r_idx, row in enumerate(board_data):
        cols = st.columns(st.session_state.board_size)
        for c_idx, cell in enumerate(row):
            button_key = f"{'player' if is_player_board else 'computer'}_{r_idx}_{c_idx}"
            if is_player_board and st.session_state.player_ship_position == (r_idx, c_idx):
                display_char = '⛵'
            elif is_player_board and (r_idx, c_idx) in st.session_state.computer_guesses:
                if (r_idx, c_idx) == st.session_state.player_ship_position:
                    display_char = '🔥'
                else:
                    display_char = 'X'
            elif not is_player_board and (r_idx, c_idx) in st.session_state.player_guesses:
                if (r_idx, c_idx) in st.session_state.computer_ship_positions:
                    display_char = '💥'
                else:
                    display_char = 'X'
            else:
                display_char = '~'

            # For player's board, show their ship if placed
            if click_handler and not st.session_state.game_over:
                if cols[c_idx].button(display_char, key=button_key, help=f"Click to {'place ship' if st.session_state.game_phase == 'player_place_ship' else 'guess'}"):
                    click_handler(r_idx, c_idx)
            else:
                cols[c_idx].markdown(f"<div style='text-align: center; border: 1px solid #ccc; padding: 5px;'>{display_char}</div>", unsafe_allow_html=True)


# --- Game Logic Functions --- #
def player_place_ship_handler(row, col):
    if st.session_state.player_ship_position is None:
        st.session_state.player_ship_position = (row, col)
        st.session_state.player_board[row][col] = '⛵' # Visual representation
        st.session_state.message = f"Your ship placed at ({row}, {col}). Time to find the computer's ships!"
        st.session_state.game_phase = "player_turn"
        st.rerun()

def handle_player_guess(row, col):
    if st.session_state.game_over or (row, col) in st.session_state.player_guesses:
        return

    st.session_state.current_turn += 1
    st.session_state.player_guesses.add((row, col))

    if (row, col) in st.session_state.computer_ship_positions:
        st.session_state.message = f"Hit! You hit a computer's ship at ({row}, {col})!"
        st.session_state.computer_board[row][col] = '💥'
        st.session_state.player_sunk_computer_ships += 1
        if st.session_state.player_sunk_computer_ships == len(st.session_state.computer_ship_positions):
            st.session_state.message = "Congratulations! You sunk all computer's battleships! You win!"
            st.session_state.game_over = True
            st.session_state.winner = "Player"
    else:
        st.session_state.message = f"Miss! You missed at ({row}, {col})."
        st.session_state.computer_board[row][col] = 'X'

    if not st.session_state.game_over:
        st.session_state.game_phase = "computer_turn"
    st.rerun()

def computer_turn():
    if st.session_state.game_over: return

    # Simple AI: random guess, no repeated guesses
    while True:
        guess_row = random.randint(0, st.session_state.board_size - 1)
        guess_col = random.randint(0, st.session_state.board_size - 1)
        if (guess_row, guess_col) not in st.session_state.computer_guesses:
            st.session_state.computer_guesses.add((guess_row, guess_col))
            break

    if (guess_row, guess_col) == st.session_state.player_ship_position:
        st.session_state.message = f"Oh no! Computer hit your ship at ({guess_row}, {guess_col})!"
        st.session_state.player_board[guess_row][guess_col] = '🔥'
        st.session_state.computer_sunk_player_ships = 1
        st.session_state.message += " The computer sunk your battleship! Computer wins!"
        st.session_state.game_over = True
        st.session_state.winner = "Computer"
    else:
        st.session_state.message = f"Computer missed your ship at ({guess_row}, {guess_col})."
        st.session_state.player_board[guess_row][guess_col] = 'X'

    if st.session_state.current_turn >= st.session_state.max_turns and not st.session_state.game_over:
        st.session_state.message = "Game over! Out of turns. No one won!"
        st.session_state.game_over = True
        st.session_state.winner = "None"

    if not st.session_state.game_over:
        st.session_state.game_phase = "player_turn"
    st.rerun()


# --- Streamlit App Layout --- #
st.title("🌊 Battleship: Player vs. Computer 🤖")

if 'game_phase' not in st.session_state:
    initialize_game()

st.info(st.session_state.message)

if st.session_state.game_phase == "player_place_ship":
    st.write("Click a square on your board below to place your ship (1 square).")
    display_board(st.session_state.player_board, player_place_ship_handler, is_player_board=True)

elif st.session_state.game_phase == "player_turn":
    st.write("It's your turn to guess! Click a square on the computer's board.")
    display_board(st.session_state.computer_board, handle_player_guess, is_player_board=False)
    st.markdown("--- ")
    st.write("Your Board (Computer's view):")
    display_board(st.session_state.player_board, is_player_board=True)

elif st.session_state.game_phase == "computer_turn":
    st.write("Computer is making its move...")
    # Execute the computer's turn logic immediately
    computer_turn()
    # After computer_turn() executes, it will have updated the state and called st.rerun()
    # So, we just need to display the updated boards based on the new state
    display_board(st.session_state.player_board, is_player_board=True)
    st.markdown("--- ")
    st.write("Computer's Board (Your view):")
    display_board(st.session_state.computer_board, is_player_board=False)

elif st.session_state.game_over:
    st.markdown(f"## Game Over! Winner: {st.session_state.winner}")
    st.markdown("### Final Boards:")
    st.markdown("Your Board:")
    display_board(st.session_state.player_board, is_player_board=True)
    st.markdown("Computer's Board (revealed):")
    # Reveal computer's ships at the end
    final_computer_board = [[cell for cell in row] for row in st.session_state.computer_board]
    for r, c in st.session_state.computer_ship_positions:
        if final_computer_board[r][c] == '~': # Only reveal if not already hit
            final_computer_board[r][c] = '🚢'
    display_board(final_computer_board, is_player_board=False)


if st.button("Reset Game"):
    initialize_game()
    st.rerun()

# Removed the 'computer_turn_processing' blocks as they are no longer needed.
# The computer_turn() function is now called directly when game_phase is "computer_turn".
