import random
import streamlit as st

class SudokuGame:
    def __init__(self, difficulty='Medium'):
        self.difficulty = difficulty
        if 'board' not in st.session_state or st.session_state.get('current_diff') != difficulty:
            self.generate_game()
            st.session_state['current_diff'] = difficulty

    def generate_game(self):
        board = [[0]*9 for _ in range(9)]
        # Fill diagonal 3x3 boxes
        for i in range(0, 9, 3):
            self.fill_box(board, i, i)
        
        self.solve(board)
        solved_board = [row[:] for row in board]
        
        # Remove cells based on difficulty
        removals = {'Easy': 30, 'Medium': 45, 'Hard': 55}.get(self.difficulty, 45)
        cells_removed = 0
        while cells_removed < removals:
            r, c = random.randint(0, 8), random.randint(0, 8)
            if board[r][c] != 0:
                board[r][c] = 0
                cells_removed += 1

        st.session_state['board'] = board
        st.session_state['solved_board'] = solved_board
        st.session_state['initial_board'] = [row[:] for row in board]

    def fill_box(self, b, row, col):
        num = list(range(1, 10))
        random.shuffle(num)
        idx = 0
        for i in range(3):
            for j in range(3):
                b[row+i][col+j] = num[idx]
                idx += 1

    def solve(self, b):
        find = self.find_empty(b)
        if not find:
            return True
        row, col = find

        for i in range(1, 10):
            if self.is_valid(b, i, (row, col)):
                b[row][col] = i
                if self.solve(b):
                    return True
                b[row][col] = 0
        return False

    def is_valid(self, b, num, pos):
        if num in b[pos[0]]:
            return False
        if num in [b[i][pos[1]] for i in range(9)]:
            return False
        box_x, box_y = pos[1] // 3, pos[0] // 3
        for i in range(box_y*3, box_y*3 + 3):
            for j in range(box_x*3, box_x*3 + 3):
                if b[i][j] == num and (i, j) != pos:
                    return False
        return True

    def find_empty(self, b):
        for i in range(9):
            for j in range(9):
                if b[i][j] == 0:
                    return (i, j)
        return None

# App UI Layout
st.set_page_config(page_title="Sudoku Game", page_icon="🔢", layout="centered")

st.title("🔢 Interactive Sudoku Game")
st.write("Fill in the grid so that every row, column, and 3x3 box contains the numbers 1 through 9.")

# Sidebar for controls
st.sidebar.header("Game Settings")
difficulty = st.sidebar.selectbox("Select Difficulty:", ["Easy", "Medium", "Hard"], index=1)

if st.sidebar.button("New Game"):
    st.session_state.pop('board', None)
    st.session_state.pop('current_diff', None)

game = SudokuGame(difficulty=difficulty)

board = st.session_state['board']
initial_board = st.session_state['initial_board']
solved_board = st.session_state['solved_board']

# Custom CSS to style the Sudoku grid with thicker 3x3 borders
st.markdown("""
    <style>
    .stNumberInput input {
        text-align: center;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Render the 9x9 Sudoku Grid
with st.container():
    for r in range(9):
        cols = st.columns(9)
        for c in range(9):
            with cols[c]:
                # Check if it's a pre-filled initial cell
                is_initial = initial_board[r][c] != 0
                
                if is_initial:
                    st.text_input(
                        f"cell_{r}_{c}",
                        value=str(initial_board[r][c]),
                        disabled=True,
                        key=f"init_{r}_{c}",
                        label_visibility="collapsed"
                    )
                else:
                    current_val = board[r][c]
                    val_str = str(current_val) if current_val != 0 else ""
                    
                    # User input field
                    new_val = st.text_input(
                        f"cell_{r}_{c}",
                        value=val_str,
                        max_chars=1,
                        key=f"input_{r}_{c}",
                        label_visibility="collapsed"
                    )
                    
                    # Update board state on input
                    if new_val.isdigit() and 1 <= int(new_val) <= 9:
                        board[r][c] = int(new_val)
                    elif new_val == "":
                        board[r][c] = 0

# Check for win condition
if not game.find_empty(board):
    if board == solved_board:
        st.balloons()
        st.success("🎉 Congratulations! You successfully solved the puzzle!")
    else:
        st.error("❌ The board is full, but there are some mistakes. Keep trying!")