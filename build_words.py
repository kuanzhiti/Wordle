import urllib.request

# Public domain dictionary of clean English words
WORD_LIST_URL = "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"

def build_word_lists():
    print("Downloading master word list...")
    req = urllib.request.urlopen(WORD_LIST_URL)
    raw_text = req.read().decode('utf-8')
    
    # Split by lines and strip whitespace
    all_lines = raw_text.splitlines()
    print(f"Total raw lines fetched: {len(all_lines)}")

    # Filter clean alphabetic words
    for length in [4, 5, 6]:
        filtered_words = sorted(list(set(
            word.strip().upper() for word in all_lines 
            if len(word.strip()) == length and word.strip().isalpha()
        )))
        
        filename = f"allowed_{length}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(filtered_words))
            
        print(f"Saved {len(filtered_words)} words to {filename}")

if __name__ == "__main__":
    build_word_lists()

SOURCES = {
    4: "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa.txt",
    5: "https://raw.githubusercontent.com/tabatkins/wordle-list/main/words", # Official Wordle answer list
    6: "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english-usa.txt"
}

def build_target_lists():
    print("Building curated target lists...")

    for length in [4, 5, 6]:
        url = SOURCES[length]
        print(f"Fetching common {length}-letter words...")
        req = urllib.request.urlopen(url)
        raw_words = req.read().decode('utf-8').splitlines()

        # Filter for exact length and alphabetical characters
        targets = sorted(list(set(
            w.strip().upper() for w in raw_words
            if len(w.strip()) == length and w.strip().isalpha()
        )))

        filename = f"targets_{length}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(targets))

        print(f"Saved {len(targets)} common words to {filename}")

if __name__ == "__main__":
    build_target_lists()