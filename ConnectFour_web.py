import streamlit as st
from easyAI import AI_Player, SSS, Human_Player

try:
    import numpy as np
except ImportError:
    st.error("Sorry, this example requires Numpy installed!")
    raise

from easyAI import TwoPlayerGame

class ConnectFour(TwoPlayerGame):
    def __init__(self, players, board=None):
        self.players = players
        self.board = (
            board
            if (board is not None)
            else (np.array([[0 for i in range(7)] for j in range(6)]))
        )
        self.current_player = 1  # player 1 starts.

    def possible_moves(self):
        return [i for i in range(7) if (self.board[:, i].min() == 0)]

    def make_move(self, column):
        line = np.max(np.where(self.board[:, column] == 0))
        self.board[line, column] = self.current_player

    def show(self):
        st.text(
            "\n"
            + "\n".join(
                ["0 1 2 3 4 5 6", 13 * "-"]
                + [
                    " ".join([[".", "O", "X"][self.board[5 - j][i]] for i in range(7)])
                    for j in range(6)
                ]
            )
        )

    def lose(self):
        return find_four(self.board, self.opponent_index)

    def win(self):
        return find_four(self.board, self.current_player)

    def is_over(self):
        return (self.board.min() > 0) or self.win() or self.lose()

    def scoring(self):
        return -100 if self.lose() else 100 if self.win() else 0


def find_four(board, current_player):
    """
    Returns True iff the player has connected 4 (or more)
    This is much faster if written in C or Cython
    """
    for pos, direction in POS_DIR:
        streak = 0
        while (0 <= pos[0] <= 5) and (0 <= pos[1] <= 6):
            if board[tuple(pos)] == current_player:
                streak += 1
                if streak == 4:
                    return True
            else:
                streak = 0
            pos = pos + direction
    return False


POS_DIR = np.array(
    [[[i, 0], [0, 1]] for i in range(6)]
    + [[[0, i], [1, 0]] for i in range(7)]
    + [[[i, 0], [1, 1]] for i in range(1, 3)]
    + [[[0, i], [1, 1]] for i in range(4)]
    + [[[i, 6], [1, -1]] for i in range(1, 3)]
    + [[[0, i], [1, -1]] for i in range(3, 7)]
)

def main():
    st.title("Connect Four")
    ai_algo_sss = SSS(5)
    game = ConnectFour([Human_Player(), AI_Player(ai_algo_sss)])

    if 'board' not in st.session_state:
        st.session_state.board = game.board
        st.session_state.current_player = game.current_player
        st.session_state.is_over = False
        st.session_state.status = ""
        st.session_state.ai_player = AI_Player(ai_algo_sss)

    def reset_board():
        st.session_state.board = np.array([[0 for i in range(7)] for j in range(6)])
        st.session_state.current_player = 1
        st.session_state.is_over = False
        st.session_state.status = ""

    def make_move(column):
        if column in game.possible_moves() and not st.session_state.is_over:
            game.board = st.session_state.board
            game.current_player = st.session_state.current_player

            line = np.max(np.where(st.session_state.board[:, column] == 0))
            st.session_state.board[line, column] = st.session_state.current_player
            game.board = st.session_state.board
            if game.win():
                st.session_state.status = "You win!"
                st.session_state.is_over = True
            elif game.is_over():
                st.session_state.status = "Draw!"
                st.session_state.is_over = True
            else:
                st.session_state.current_player = 3 - st.session_state.current_player

            game.board = st.session_state.board
            game.current_player = st.session_state.current_player

            if not st.session_state.is_over:
                ai_move = st.session_state.ai_player.ask_move(game)
                line = np.max(np.where(st.session_state.board[:, ai_move] == 0))
                st.session_state.board[line, ai_move] = st.session_state.current_player
                game.board = st.session_state.board
                if game.lose():
                    st.session_state.status = "AI wins!"
                    st.session_state.is_over = True
                elif game.win():  # Add this condition
                    st.session_state.status = "AI wins!"
                    st.session_state.is_over = True
                elif game.is_over():
                    st.session_state.status = "Draw!"
                    st.session_state.is_over = True
                else:
                    st.session_state.current_player = 3 - st.session_state.current_player

    
    if st.button("↺", key="restart_button"):
        reset_board()

   

    st.text(st.session_state.status)

    for row in range(6):
        cols = st.columns(7)
        for col in range(7):
            cell = st.session_state.board[row, col]
            if cell == 0:
                cols[col].button(" ", key=f"{row}_{col}", on_click=make_move, args=(col,))
            else:
                color = "yellow" if cell == 1 else "red"
                cols[col].markdown(f'<div style="width:40px;height:40px;background-color:{color};border-radius:50%;"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <style>

        div[data-testid="stButton"] button {
            border-radius: 100%;
            width: 40px;
            height: 40px;
            padding: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
