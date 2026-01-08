import requests
import subprocess
import os
import re

# Function to read API_KEY from a decrypted .env.gpg
def get_api_key(gpg_file_path=".env.gpg"):
    result = subprocess.run(
        ["gpg", "--quiet", "--batch", "--yes", "--decrypt", gpg_file_path],
        capture_output=True,
        text=True
    )
    env_content = result.stdout

    for line in env_content.splitlines():
        if line.startswith("API_KEY="):
            return line.split("=", 1)[1].strip()
    raise ValueError("API_KEY not found in .env.gpg")

API_KEY = get_api_key()

conversation = []

def sysprompt(system_text):
    global conversation
    conversation = [{"role": "system", "content": system_text}]
    return f"System prompt set: {system_text}"

def render_markdown_terminal(text):
    """
    Replace Markdown syntax with ANSI escape codes for terminal rendering.
    - **bold** -> bold
    - *italic* -> italic
    - `code` -> inverted background
    """
    # Bold: **text**
    text = re.sub(r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", text)
    # Italic: *text*
    text = re.sub(r"\*(.*?)\*", r"\033[3m\1\033[0m", text)
    # Inline code: `code`
    text = re.sub(r"`(.*?)`", r"\033[7m\1\033[0m", text)
    return text

def prompt(user_text):
    global conversation
    conversation.append({"role": "user", "content": user_text})

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "xiaomi/mimo-v2-flash:free",
            "messages": conversation
        }
    )

    data = response.json()
    reply = data['choices'][0]['message']['content']
    conversation.append({"role": "assistant", "content": reply})

    return render_markdown_terminal(reply)

class characters:
    @staticmethod
    def cat():
        return sysprompt("You ARE a cat. Respond like a realistic cat would.")

    @staticmethod
    def dog():
        return sysprompt("You ARE a dog. Respond like a realistic dog would.")

    @staticmethod
    def david():
        return sysprompt("You ARE a random person named David. Respond like David would.")