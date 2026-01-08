import vai
import re
import time
import sys
import webbrowser

# --- Terminal-style Markdown renderer ---
def render_terminal(text):
    """
    Convert Markdown to ANSI escape codes:
    - **bold** -> bold
    - *italic* -> italic
    - `code` -> inverted colors
    """
    text = re.sub(r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", text)
    text = re.sub(r"\*(.*?)\*", r"\033[3m\1\033[0m", text)
    text = re.sub(r"`(.*?)`", r"\033[7m\1\033[0m", text)
    return text

# --- Typing effect ---
def type_out(text, delay=0.01):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print("\n")

# --- Character selection with search ---
def select_character():
    all_chars = {
        "Cat": vai.characters.cat,
        "Dog": vai.characters.dog,
        "David": vai.characters.david,
        "Submit a character": lambda: webbrowser.open_new_tab("https://forms.gle/rZZhSFfB5CWLuid79")
    }

    print("Search for a character (type part of the name):")
    search_term = input("> ").strip().lower()

    matches = {name: func for name, func in all_chars.items() if search_term in name.lower()}

    if not matches:
        print("No characters found. Defaulting to Cat.")
        return "Cat", vai.characters.cat

    print("Select a character:")
    for i, name in enumerate(matches.keys(), start=1):
        print(f"{i}: {name}")

    choice = input("Choice (number): ").strip()
    try:
        choice = int(choice)
        selected_name = list(matches.keys())[choice - 1]
        return selected_name, matches[selected_name]
    except:
        print("Invalid choice. Defaulting to first match.")
        selected_name = list(matches.keys())[0]
        return selected_name, matches[selected_name]

# --- Main loop ---
def main():
    char_name, char_func = select_character()
    char_func()
    print(f"Switched to {char_name}\n")

    while True:
        user_text = input("\033[92mYou:\033[0m ")  # green prompt
        if user_text.lower() in ["quit", "exit"]:
            break
        response = vai.prompt(user_text)
        response_ansi = render_terminal(response)
        type_out(f"\033[93m{char_name}:\033[0m {response_ansi}")  # yellow AI name

if __name__ == "__main__":
    main()
