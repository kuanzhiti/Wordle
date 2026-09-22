from game_engine import WordleEngine

def test_run():
    engine = WordleEngine()
    
    # 1. Select Word Length (4, 5, or 6)
    mode = int(input("Select word length (4, 5, or 6): "))
    engine.start_new_game(length=mode, max_attempts=6)

    print(f"\n--- Starting {mode}-Letter Wordle ---")
    
    while not engine.is_game_over:
        guess = input(f"Attempt {engine.current_attempt + 1}/6 - Enter guess: ").strip()
        
        valid, colors, msg = engine.evaluate_guess(guess)
        if not valid:
            print(f" Invalid: {msg}")
            continue

        # Format colored output in terminal
        feedback = []
        for char, color in zip(guess.upper(), colors):
            if color == "green":
                feedback.append(f"[{char}:GREEN]")
            elif color == "yellow":
                feedback.append(f"[{char}:YELLOW]")
            else:
                feedback.append(f"[{char}:GREY]")
                
        print(" -> " + " ".join(feedback))

    if engine.is_won:
        print(f"\n🎉 You won in {engine.current_attempt} attempts!")
    else:
        print(f"\n❌ Game Over! The secret word was: {engine.target_word}")

if __name__ == "__main__":
    test_run()