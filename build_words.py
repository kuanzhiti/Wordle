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