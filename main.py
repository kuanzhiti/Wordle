import sys
from typing import Dict, List
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QComboBox, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QKeyEvent

from game_engine import WordleEngine, LetterState


class WordleWindow(QMainWindow):
    # CSS Color Constants
    COLOR_DEFAULT_BG = "#FFFFFF"
    COLOR_DEFAULT_BORDER = "#D3D6DA"
    COLOR_ACTIVE_BORDER = "#878A8C"
    COLOR_TEXT_DARK = "#1A1A1B"
    COLOR_TEXT_LIGHT = "#FFFFFF"
    
    COLOR_GREEN = "#6AAA64"
    COLOR_YELLOW = "#C9B458"
    COLOR_GREY = "#787C7E"
    COLOR_KEY_BG = "#D3D6DA"

    KEYBOARD_LAYOUT = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "⌫"]
    ]

    def __init__(self):
        super().__init__()
        self.engine = WordleEngine()
        
        # Ensure window receives key events
        self.setFocusPolicy(Qt.StrongFocus)
        
        # UI State Tracking
        self.current_row = 0
        self.current_col = 0
        self.current_guess: List[str] = []
        
        self.grid_labels: List[List[QLabel]] = []
        self.key_buttons: Dict[str, QPushButton] = {}
        self.key_states: Dict[str, str] = {}

        self.init_ui()
        self.start_new_game(length=5)

    def init_ui(self):
        self.setWindowTitle("Python PyQt5 Wordle")
        self.setMinimumSize(520, 720)
        self.setStyleSheet(f"background-color: {self.COLOR_DEFAULT_BG};")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(12)

        # 1. Header
        self.create_header()

        # 2. Status Banner
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #E74C3C; min-height: 24px;"
        )
        self.main_layout.addWidget(self.status_label)

        # 3. Dynamic Grid Area
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(6)
        self.grid_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.grid_container, stretch=1)

        # 4. Virtual Keyboard
        self.keyboard_container = QWidget()
        self.keyboard_layout = QVBoxLayout(self.keyboard_container)
        self.keyboard_layout.setSpacing(6)
        self.keyboard_layout.setContentsMargins(0, 10, 0, 10)
        self.main_layout.addWidget(self.keyboard_container)

        self.create_keyboard()

    def create_header(self):
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("WORDLE")
        title_label.setStyleSheet(
            f"font-size: 32px; font-weight: 800; color: {self.COLOR_TEXT_DARK}; letter-spacing: 2px;"
        )

        # Mode Selection Dropdown
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["4 Letters", "5 Letters", "6 Letters"])
        self.mode_combo.setCurrentIndex(1)
        self.mode_combo.setFocusPolicy(Qt.NoFocus)  # <--- Prevent stealing focus
        self.mode_combo.setStyleSheet("""
            QComboBox {
                padding: 6px 12px;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #D3D6DA;
                border-radius: 6px;
                background-color: white;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)

        # New Game Button
        reset_btn = QPushButton("New Game")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setFocusPolicy(Qt.NoFocus)  # <--- Prevent stealing focus
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COLOR_TEXT_DARK};
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: #3A3A3C;
            }}
        """)
        reset_btn.clicked.connect(lambda: self.start_new_game(self.engine.word_length))

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.mode_combo)
        header_layout.addWidget(reset_btn)

        self.main_layout.addWidget(header_widget)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #E5E7EB;")
        self.main_layout.addWidget(divider)

    def create_grid(self, length: int):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.grid_labels = []
        cell_size = 62 if length == 4 else (56 if length == 5 else 50)

        for row in range(self.engine.max_attempts):
            row_labels = []
            for col in range(length):
                lbl = QLabel("")
                lbl.setFixedSize(QSize(cell_size, cell_size))
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setFont(QFont("Arial", 22, QFont.Bold))
                self.set_tile_style(lbl, "empty")
                
                self.grid_layout.addWidget(lbl, row, col)
                row_labels.append(lbl)
            self.grid_labels.append(row_labels)

    def set_tile_style(self, label: QLabel, state: str, letter: str = ""):
        if letter:
            label.setText(letter.upper())

        if state == "empty":
            label.setStyleSheet(f"""
                QLabel {{
                    border: 2px solid {self.COLOR_DEFAULT_BORDER};
                    background-color: {self.COLOR_DEFAULT_BG};
                    color: {self.COLOR_TEXT_DARK};
                    border-radius: 4px;
                }}
            """)
        elif state == "active":
            label.setStyleSheet(f"""
                QLabel {{
                    border: 2px solid {self.COLOR_ACTIVE_BORDER};
                    background-color: {self.COLOR_DEFAULT_BG};
                    color: {self.COLOR_TEXT_DARK};
                    border-radius: 4px;
                }}
            """)
        elif state == LetterState.GREEN:
            label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.COLOR_GREEN};
                    color: {self.COLOR_TEXT_LIGHT};
                    border: none;
                    border-radius: 4px;
                }}
            """)
        elif state == LetterState.YELLOW:
            label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.COLOR_YELLOW};
                    color: {self.COLOR_TEXT_LIGHT};
                    border: none;
                    border-radius: 4px;
                }}
            """)
        elif state == LetterState.GREY:
            label.setStyleSheet(f"""
                QLabel {{
                    background-color: {self.COLOR_GREY};
                    color: {self.COLOR_TEXT_LIGHT};
                    border: none;
                    border-radius: 4px;
                }}
            """)

    def create_keyboard(self):
        while self.keyboard_layout.count():
            item = self.keyboard_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.key_buttons.clear()

        for row_keys in self.KEYBOARD_LAYOUT:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(5)
            row_layout.setAlignment(Qt.AlignCenter)

            for key in row_keys:
                btn = QPushButton(key)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setFocusPolicy(Qt.NoFocus)  # <--- Prevent stealing focus
                
                if key in ("ENTER", "⌫"):
                    btn.setFixedWidth(64)
                    btn.setFont(QFont("Arial", 11, QFont.Bold))
                else:
                    btn.setFixedWidth(40)
                    btn.setFont(QFont("Arial", 14, QFont.Bold))

                btn.setFixedHeight(54)
                self.update_key_style(btn, self.COLOR_KEY_BG, self.COLOR_TEXT_DARK)
                btn.clicked.connect(lambda checked, k=key: self.handle_key_input(k))
                
                self.key_buttons[key] = btn
                row_layout.addWidget(btn)

            self.keyboard_layout.addWidget(row_widget)

    def update_key_style(self, btn: QPushButton, bg_color: str, text_color: str):
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 4px;
                border: none;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
        """)

    def on_mode_changed(self, index: int):
        mode_lengths = [4, 5, 6]
        selected_length = mode_lengths[index]
        self.start_new_game(selected_length)

    def start_new_game(self, length: int):
        self.engine.start_new_game(length=length, max_attempts=6)
        self.current_row = 0
        self.current_col = 0
        self.current_guess = []
        self.key_states.clear()
        self.status_label.setText("")

        self.create_grid(length)

        for key, btn in self.key_buttons.items():
            self.update_key_style(btn, self.COLOR_KEY_BG, self.COLOR_TEXT_DARK)

        # Re-assign keyboard focus to main window
        self.setFocus()  # <--- Always focus window on start

    # --- Input Handling ---

    def keyPressEvent(self, event: QKeyEvent):
        if self.engine.is_game_over:
            return

        key_code = event.key()

        if Qt.Key_A <= key_code <= Qt.Key_Z:
            char = chr(key_code).upper()
            self.handle_character(char)
        elif key_code in (Qt.Key_Backspace, Qt.Key_Delete):
            self.handle_backspace()
        elif key_code in (Qt.Key_Return, Qt.Key_Enter):
            self.handle_enter()

    def handle_key_input(self, key_text: str):
        if self.engine.is_game_over:
            return

        if key_text == "ENTER":
            self.handle_enter()
        elif key_text == "⌫":
            self.handle_backspace()
        else:
            self.handle_character(key_text)

    def handle_character(self, char: str):
        if self.current_col < self.engine.word_length:
            lbl = self.grid_labels[self.current_row][self.current_col]
            self.set_tile_style(lbl, "active", char)
            self.current_guess.append(char)
            self.current_col += 1
            self.status_label.setText("")

    def handle_backspace(self):
        if self.current_col > 0:
            self.current_col -= 1
            self.current_guess.pop()
            lbl = self.grid_labels[self.current_row][self.current_col]
            lbl.setText("")
            self.set_tile_style(lbl, "empty")
            self.status_label.setText("")

    def handle_enter(self):
        if len(self.current_guess) < self.engine.word_length:
            self.status_label.setText("Not enough letters!")
            return

        guess_str = "".join(self.current_guess)
        valid, colors, msg = self.engine.evaluate_guess(guess_str)

        if not valid:
            self.status_label.setText(msg)
            return

        for col, color in enumerate(colors):
            lbl = self.grid_labels[self.current_row][col]
            self.set_tile_style(lbl, color)

        self.update_keyboard_colors(guess_str, colors)

        if self.engine.is_won:
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #6AAA64;")
            self.status_label.setText("🎉 Splendid! You guessed the word!")
            QMessageBox.information(self, "Victory!", f"Splendid! You guessed '{self.engine.target_word}'!")
            self.setFocus()
        elif self.engine.is_game_over:
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #787C7E;")
            self.status_label.setText(f"Game Over! The word was: {self.engine.target_word}")
            QMessageBox.warning(self, "Game Over", f"Out of attempts! The correct word was '{self.engine.target_word}'.")
            self.setFocus()
        else:
            self.current_row += 1
            self.current_col = 0
            self.current_guess = []

    def update_keyboard_colors(self, guess: str, colors: List[str]):
        color_map = {
            LetterState.GREEN: (self.COLOR_GREEN, self.COLOR_TEXT_LIGHT, 3),
            LetterState.YELLOW: (self.COLOR_YELLOW, self.COLOR_TEXT_LIGHT, 2),
            LetterState.GREY: (self.COLOR_GREY, self.COLOR_TEXT_LIGHT, 1),
        }

        for char, color in zip(guess, colors):
            if char in self.key_buttons:
                current_state = self.key_states.get(char, None)
                new_priority = color_map[color][2]
                
                current_priority = color_map[current_state][2] if current_state else 0
                if new_priority > current_priority:
                    self.key_states[char] = color
                    bg, text_clr, _ = color_map[color]
                    self.update_key_style(self.key_buttons[char], bg, text_clr)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordleWindow()
    window.show()
    sys.exit(app.exec_())