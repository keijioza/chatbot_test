# chatbot_test# Terminal Chatbot

A simple chatbot you can run directly in your terminal — built in **pure Python** with **no external dependencies**.

## Features

* **Small talk**: greetings, thanks, goodbyes.
* **Memory**: learns your name when you say "my name is ...".
* **Time & date**: ask for the current time/date.
* **Jokes**: type "joke" and get a random one.
* **Calculator**: evaluate safe math expressions (`calc: 2*(3+4)` or `calc sqrt(16)`).
* **Facts**: simple built-in facts (Python, OpenAI, Manila, planets).
* **Mood detection**: responds to words like "sad" or "happy".
* **Commands**:

  * `/help` — show usage guide
  * `/reset` — clear history but keep your name
  * `/save <file>` — save memory/history to JSON
  * `/load <file>` — load memory/history from JSON
  * `/quit` — exit the chatbot

## Requirements

* Python **3.9+**
* Works on Linux, macOS, or Windows terminal

## Installation

1. Save the chatbot file:

   ```bash
   wget https://raw.githubusercontent.com/your-repo/chatbot.py
   ```

   *(or just copy the `chatbot.py` file into your project folder)*

2. Make it executable (optional, Linux/macOS):

   ```bash
   chmod +x chatbot.py
   ```

## Usage

Run the chatbot:

```bash
python chatbot.py
```

### Example session

```
:> hi
Hey! I'm 🤖 — ask me stuff or type /help.

:> my name is Ana
Nice to meet you, Ana! 👋

:> time
It's 2025-08-21 16:32.

:> calc: 2*(3+4)
2*(3+4) = 14

:> joke
Why did the developer go broke? Because they used up all their cache.

:> /quit
Goodbye!
```

## Notes

* All math is evaluated safely using Python's AST — only basic operators and math functions are allowed.
* Conversation history and your name can be saved/loaded to JSON for persistence.

---

Enjoy chatting with your terminal bot! 
