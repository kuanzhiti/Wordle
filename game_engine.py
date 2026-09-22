import random
from typing import List, Tuple, Dict
from collections import Counter

class LetterState:
    GREY = "grey"
    YELLOW = "yellow"
    GREEN = "green"

class WordleEngine:
    AVAILABLE_MODES = [4, 5, 6]  # Supported word lengths

    def __init__(self):
        self.word_length: int = 5
        self.max_attempts: int = 6
        self.target_word: str = ""
        
        # Dictionaries storing words for each length mode: {4: set(), 5: set(), 6: set()}
        self.allowed_words_by_len: Dict[int, set] = {}
        self.target_words_by_len: Dict[int, list] = {}

        # Active game state
        self.current_attempt: int = 0
        self.guesses: List[str] = []
        self.results: List[List[str]] = []
        self.is_game_over: bool = False
        self.is_won: bool = False

        # Load all word lists on startup
        self._load_all_word_lists()

    def _load_all_word_lists(self):
        """Loads word files for all supported lengths (4, 5, 6) into memory."""
        for length in self.AVAILABLE_MODES:
            # Load allowed guesses
            try:
                with open(f"allowed_{length}.txt", "r", encoding="utf-8") as f:
                    self.allowed_words_by_len[length] = set(
                        line.strip().upper() for line in f if line.strip()
                    )
            except FileNotFoundError:
                print(f"[Warning] allowed_{length}.txt not found!")
                self.allowed_words_by_len[length] = set()

            # Load secret target words
            try:
                with open(f"targets_{length}.txt", "r", encoding="utf-8") as f:
                    self.target_words_by_len[length] = [
                        line.strip().upper() for line in f if line.strip()
                    ]
            except FileNotFoundError:
                print(f"[Warning] targets_{length}.txt not found!")
                self.target_words_by_len[length] = []

    def start_new_game(self, length: int = 5, max_attempts: int = 6):
        """
        Starts a new game for the selected character length (4, 5, or 6)
        and max guess attempts.
        """
        if length not in self.AVAILABLE_MODES:
            raise ValueError(f"Invalid mode: {length}. Choose from {self.AVAILABLE_MODES}.")

        self.word_length = length
        self.max_attempts = max_attempts

        # Pick random word from target pool for this length
        targets = self.target_words_by_len.get(length, [])
        if not targets:
            raise RuntimeError(f"No target words loaded for {length}-letter mode!")

        self.target_word = random.choice(targets)

        # Reset active game counters
        self.current_attempt = 0
        self.guesses = []
        self.results = []
        self.is_game_over = False
        self.is_won = False

        print(f"[DEBUG] Started {length}-Letter Wordle ({max_attempts} attempts). Target: {self.target_word}")

    @property
    def current_allowed_words(self) -> set:
        """Returns the set of allowed words for the active word length."""
        return self.allowed_words_by_len.get(self.word_length, set())

    @property
    def current_target_words(self) -> list:
        """Returns the list of target words for the active word length."""
        return self.target_words_by_len.get(self.word_length, [])

    def is_valid_word(self, guess: str) -> bool:
        """Checks if guess length matches active mode and exists in dictionaries."""
        guess = guess.upper()
        if len(guess) != self.word_length:
            return False
        
        return (
            guess in self.current_allowed_words 
            or guess in self.current_target_words
        )

    def evaluate_guess(self, guess: str) -> Tuple[bool, List[str], str]:
        """
        Evaluates a guess against target word.
        Returns: (is_valid, list_of_colors, error_message)
        """
        guess = guess.upper()

        if self.is_game_over:
            return False, [], "Game is already over."

        if len(guess) != self.word_length:
            return False, [], f"Guess must be exactly {self.word_length} letters!"

        if not self.is_valid_word(guess):
            return False, [], f"'{guess}' is not in the dictionary!"

        # Initialize result array with GREY
        result = [LetterState.GREY] * self.word_length
        target_counts = Counter(self.target_word)

        # PASS 1: Identify GREEN matches
        for i in range(self.word_length):
            if guess[i] == self.target_word[i]:
                result[i] = LetterState.GREEN
                target_counts[guess[i]] -= 1

        # PASS 2: Identify YELLOW matches
        for i in range(self.word_length):
            if result[i] != LetterState.GREEN:
                char = guess[i]
                if target_counts.get(char, 0) > 0:
                    result[i] = LetterState.YELLOW
                    target_counts[char] -= 1

        # Update State
        self.guesses.append(guess)
        self.results.append(result)
        self.current_attempt += 1

        if guess == self.target_word:
            self.is_won = True
            self.is_game_over = True
        elif self.current_attempt >= self.max_attempts:
            self.is_game_over = True

        return True, result, ""