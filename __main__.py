import re
import time
import sys
import webbrowser

# Optional: color support on Windows
try:
    from colorama import init as colorama_init
    colorama_init()
except Exception:
    pass  # colorama is optional; ANSI may still work on many terminals

# --- Terminal-style Markdown renderer ---
def render_terminal(text):
    """
    Convert a few Markdown-like syntaxes to ANSI:
    - **bold** -> bold
    - *italic* -> italic
    - `code` -> inverted colors
    """
    # Use non-greedy matches and DOTALL so newlines are handled.
    text = re.sub(r"\*\*(.+?)\*\*", r"\033[1m\1\033[0m", text, flags=re.DOTALL)
    text = re.sub(r"\*(.+?)\*", r"\033[3m\1\033[0m", text, flags=re.DOTALL)
    text = re.sub(r"`(.+?)`", r"\033[7m\1\033[0m", text, flags=re.DOTALL)
    return text

# --- Typing effect ---
def type_out(text, delay=0.01):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()  # newline

# --- Prompt helper ---
def instructioninput(prompt_text="Enter the instruction: "):
    """
    Return the user's input (so caller can use it).
    """
    try:
        return input(prompt_text)
    except EOFError:
        return ""

# --- Character selection with search ---
def select_character(vai):
    """
    Show a small search UI and return (name, callable).
    The callable, when invoked, should switch the character context (matching your original intent).
    """
    # Prepare a mapping of display name -> action (callable)
    all_chars = {
        "Cat": lambda: getattr(vai.characters, "cat")(),    # call the character switcher
        "Dog": lambda: getattr(vai.characters, "dog")(),
        "David": lambda: getattr(vai.characters, "david")(),
        "Submit a character": lambda: webbrowser.open_new_tab("https://forms.gle/rZZhSFfB5CWLuid79"),
        # "Custom Prompt" will be handled specially below.
    }

    print("Search for a character (type part of the name). Leave blank to list all:")
    search_term = input("> ").strip().lower()

    # Find matching names
    matches = {name: action for name, action in all_chars.items() if search_term in name.lower()}

    # Always add Custom Prompt as an option
    matches["Custom Prompt"] = None

    if not matches:
        print("No characters found. Defaulting to Cat.")
        return "Cat", all_chars["Cat"]

    # List matches
    print("Select a character:")
    for i, name in enumerate(matches.keys(), start=1):
        print(f"{i}: {name}")

    choice = input("Choice (number): ").strip()
    try:
        choice = int(choice)
        selected_name = list(matches.keys())[choice - 1]
    except Exception:
        print("Invalid choice. Defaulting to first match.")
        selected_name = list(matches.keys())[0]

    # Handle Custom Prompt specially
    if selected_name == "Custom Prompt":
        prompt_text = instructioninput("Enter custom system prompt (leave blank to cancel): ")
        if prompt_text:
            # If vai.sysprompt exists, call it; otherwise just print a notification.
            if hasattr(vai, "sysprompt"):
                try:
                    # Some implementations expect a string, some may return a callable; handle both
                    result = vai.sysprompt(prompt_text)
                    # If result is callable (e.g., a configured character), return it
                    if callable(result):
                        return "Custom Prompt", result
                    # otherwise return a no-op callable — we've applied the sys prompt already
                    return "Custom Prompt", (lambda: None)
                except Exception as e:
                    print(f"Warning: failed to call vai.sysprompt: {e}")
                    return "Custom Prompt", (lambda: None)
            else:
                print("vai.sysprompt not available in this environment — custom prompt captured but not applied.")
                return "Custom Prompt", (lambda: None)
        else:
            print("No custom prompt entered — defaulting to Cat.")
            return "Cat", all_chars["Cat"]

    # For other choices, ensure we return a callable (some actions may be None or not callable)
    action = matches[selected_name]
    if action is None:
        return selected_name, (lambda: None)
    return selected_name, action

# --- Main loop ---
def main():
    # Lazy import of 'vai' so this module can be imported without immediately failing if 'vai' is absent.
    try:
        import vai
    except Exception as e:
        print("Error: could not import 'vai'. Make sure the 'vai' package is installed and available.")
        print("Exception:", e)
        sys.exit(1)

    char_name, char_func = select_character(vai)

    # Attempt to switch to the chosen character (if callable)
    try:
        if callable(char_func):
            char_func()
        else:
            print(f"Selected character '{char_name}' has no callable action.")
    except Exception as e:
        print(f"Error while activating '{char_name}': {e}")

    print(f"Switched to {char_name}\n")

    try:
        while True:
            user_text = input("\033[92mYou:\033[0m ").strip()  # green prompt
            if not user_text:
                continue
            # Special commands
            if user_text.lower() in ["quit", "exit"]:
                print("Goodbye.")
                break
            if user_text.lower() in ["switch", "change", "select"]:
                char_name, char_func = select_character(vai)
                try:
                    if callable(char_func):
                        char_func()
                    print(f"Switched to {char_name}\n")
                except Exception as e:
                    print(f"Failed switching to {char_name}: {e}")
                continue

            # Generate a response via vai
            try:
                response = vai.prompt(user_text)
            except Exception as e:
                response = f"[Error calling vai.prompt: {e}]"

            response_ansi = render_terminal(response)
            type_out(f"\033[93m{char_name}:\033[0m {response_ansi}")
    except KeyboardInterrupt:
        print("\nInterrupted. Exiting.")

if __name__ == "__main__":
    main()
