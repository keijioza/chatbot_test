#!/usr/bin/env python3
"""
Terminal Chatbot — pure Python, no external dependencies.

Features:
- Small talk (hi/bye/thanks), time/date, jokes, calculator, echo, and simple facts.
- "Memory": learns your name ("my name is <name>") and recalls it later.
- Safe calculator using Python's ast (supports +,-,*,/,**, parentheses).
- Commands: /help, /reset, /save <file>, /load <file>, /quit.

Run:
  python chatbot.py

Tested with Python 3.9+.
"""

from __future__ import annotations
import ast
import math
import operator as op
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List

# -----------------------------
# Safe calculator (AST-based)
# -----------------------------
ALLOWED_OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
    ast.Mod: op.mod,
}

ALLOWED_NAMES = {k: getattr(math, k) for k in (
    "pi", "e", "tau"
)} | {k: getattr(math, k) for k in (
    "sin", "cos", "tan", "asin", "acos", "atan",
    "sqrt", "log", "log10", "exp", "floor", "ceil"
)}

def eval_expr(expr: str) -> float:
    """Safely evaluate a math expression using AST.
    Supports numbers, parentheses, + - * / ** %, and selected math functions/constants.
    """
    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Num):  # type: ignore[attr-defined]
            return node.n  # type: ignore[attr-defined]
        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
            return ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in ALLOWED_OPS:
            return ALLOWED_OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in ALLOWED_NAMES:
                fn = ALLOWED_NAMES[node.func.id]
                args = [_eval(a) for a in node.args]
                return fn(*args)
        if isinstance(node, ast.Name) and node.id in ALLOWED_NAMES:
            return ALLOWED_NAMES[node.id]
        raise ValueError("Unsupported expression")

    tree = ast.parse(expr, mode="eval")
    return _eval(tree.body)  # type: ignore[arg-type]

# -----------------------------
# Simple knowledge base
# -----------------------------
FACTS: Dict[str, str] = {
    "python": "Python is a popular programming language known for readability and versatility.",
    "openai": "OpenAI researches and builds safe, useful AI systems.",
    "manila": "Manila is the capital of the Philippines.",
    "planet": "There are eight planets in our Solar System.",
}

JOKES = [
    "Why did the developer go broke? Because they used up all their cache.",
    "I would tell you a UDP joke, but you might not get it.",
    "Debugging: being the detective in a crime movie where you are also the murderer.",
]

EMOJI = {
    "happy": "🙂",
    "sad": "🙁",
    "wave": "👋",
    "bot": "🤖",
}

NAME_PAT = re.compile(r"\bmy\s+name\s+is\s+([A-Za-z][A-Za-z\-\'\s]{0,30})\b", re.I)

# -----------------------------
# Chatbot core
# -----------------------------
class Chatbot:
    def __init__(self) -> None:
        self.memory: Dict[str, Any] = {
            "name": None,
            "history": [],  # type: ignore[var-annotated]
        }

    # ---------- utilities ----------
    def now(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M")

    def _remember_name(self, text: str) -> str | None:
        m = NAME_PAT.search(text)
        if m:
            name = m.group(1).strip().title()
            self.memory["name"] = name
            return name
        return None

    def save(self, path: str) -> str:
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
        return f"Saved conversation to {path}"

    def load(self, path: str) -> str:
        import json
        with open(path, "r", encoding="utf-8") as f:
            self.memory = json.load(f)
        return f"Loaded conversation from {path}"

    def reset(self) -> str:
        name = self.memory.get("name")
        self.memory = {"name": name, "history": []}
        return "Okay, I cleared the chat history but kept your name."

    # ---------- response logic ----------
    def respond(self, text: str) -> str:
        text = text.strip()
        if not text:
            return "Say something and I'll reply!"

        # Learn user's name
        learned = self._remember_name(text)
        if learned:
            return f"Nice to meet you, {learned}! {EMOJI['wave']}"

        low = text.lower()
        name = self.memory.get("name")

        # Greetings / thanks / bye
        if any(w in low for w in ("hello", "hi", "hey")):
            return f"Hey{' ' + name if name else ''}! I'm {EMOJI['bot']} — ask me stuff or type /help."
        if any(w in low for w in ("thank", "thanks", "ty")):
            return "You're welcome!"
        if any(w in low for w in ("bye", "goodbye", "quit", "exit")):
            return "Bye! Type /quit to leave the program."

        # Time / date
        if "time" in low or "date" in low:
            return f"It's {self.now()}."

        # Jokes
        if "joke" in low:
            import random
            return random.choice(JOKES)

        # Calculator trigger: "calc: <expr>" or startswith("calc ")
        if low.startswith("calc:") or low.startswith("calc "):
            expr = text.split(":", 1)[1] if ":" in text else text.split(" ", 1)[1]
            try:
                val = eval_expr(expr)
                return f"{expr.strip()} = {val}"
            except Exception as e:
                return f"I couldn't compute that: {e}"

        # Simple facts lookup
        for key, ans in FACTS.items():
            if key in low:
                return ans

        # Light sentiment cue
        if any(w in low for w in ("sad", "down", "tired", "stressed")):
            return f"Sorry you're feeling that way{',' if name else ''} {name or ''}. I'm here to listen. {EMOJI['sad']}"
        if any(w in low for w in ("great", "awesome", "happy", "good")):
            return f"Love to hear that{',' if name else ''} {name or ''}! {EMOJI['happy']}"

        # Echo fallback with tip
        return "I didn't quite get that. Try /help or say 'joke', 'time', or 'calc: 2*(3+4)'."

# -----------------------------
# CLI shell
# -----------------------------
HELP = f"""
Commands:
  /help                 Show this help
  /reset                Clear history (keep your name)
  /save <file>          Save memory/history to a JSON file
  /load <file>          Load memory/history from a JSON file
  /quit                 Exit

Tips:
  • Tell me your name (e.g., "my name is Sam").
  • Do quick math: "calc: 2*(3+4)" or "calc sqrt(16)".
  • Ask for a joke or the time/date.
"""


def main(argv: List[str]) -> int:
    bot = Chatbot()
    print(f"Chatbot ready {EMOJI['bot']} — type /help for tips.\n")
    while True:
        try:
            user = input(":> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return 0

        if not user:
            continue

        # Slash commands
        if user.startswith("/"):
            parts = user.split()
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else None
            if cmd == "/help":
                print(HELP)
                continue
            if cmd == "/reset":
                print(bot.reset())
                continue
            if cmd == "/save":
                if not arg:
                    print("Usage: /save <file>")
                else:
                    try:
                        print(bot.save(arg))
                    except Exception as e:
                        print(f"Couldn't save: {e}")
                continue
            if cmd == "/load":
                if not arg:
                    print("Usage: /load <file>")
                else:
                    try:
                        print(bot.load(arg))
                    except Exception as e:
                        print(f"Couldn't load: {e}")
                continue
            if cmd == "/quit":
                print("Goodbye!")
                return 0
            print("Unknown command. Type /help.")
            continue

        # Normal chat
        reply = bot.respond(user)
        print(reply)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
