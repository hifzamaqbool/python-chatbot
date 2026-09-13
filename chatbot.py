"""
Custom AI Chatbot with Memory
Uses the Gemini API (Google AI Studio) via the google-generativeai SDK.

Run:
    python chatbot.py

Requires:
    GEMINI_API_KEY environment variable (or a .env file, see README.md)
"""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv
import google.generativeai as genai

from memory_manager import MemoryManager

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
MODEL_NAME = "gemini-3.6-flash"        # current stable flash model (as of Sept 2026)
MEMORY_FILE = "memory.json"            # where conversation memory is persisted
MAX_TURNS_BEFORE_SUMMARY = 20          # summarize older turns once history grows this long
SYSTEM_PROMPT = (
    "You are a helpful, friendly personal assistant chatbot. "
    "You have long-term memory of past conversations, provided to you as "
    "context below. Use it naturally, without explicitly saying things like "
    "'according to my memory'. If you don't know something, say so."
)


def load_api_key() -> str:
    load_dotenv()  # loads variables from a .env file if present
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print(
            "ERROR: No API key found.\n"
            "Set the GEMINI_API_KEY environment variable, or create a .env "
            "file (see .env.example) with:\n\n"
            "    GEMINI_API_KEY=your_key_from_google_ai_studio\n"
        )
        sys.exit(1)
    return api_key


def build_model(api_key: str):
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
    )


def main():
    api_key = load_api_key()
    model = build_model(api_key)
    memory = MemoryManager(MEMORY_FILE, model=model, max_turns=MAX_TURNS_BEFORE_SUMMARY)

    print("=" * 60)
    print(" Gemini Chatbot with Memory")
    print(" Type 'exit' or 'quit' to stop. Type 'forget' to wipe memory.")
    print("=" * 60)

    # Start a chat session seeded with prior memory (summary + recent turns)
    chat = model.start_chat(history=memory.to_gemini_history())

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if user_input.lower() == "forget":
            memory.clear()
            chat = model.start_chat(history=[])
            print("Memory wiped clean.")
            continue

        try:
            response = chat.send_message(user_input)
            reply = response.text
        except Exception as e:
            print(f"\n[Error talking to Gemini API: {e}]")
            continue

        print(f"\nBot: {reply}")

        memory.add_turn(user_input, reply, timestamp=datetime.now().isoformat())
        memory.maybe_summarize()
        memory.save()


if __name__ == "__main__":
    main()