"""
memory_manager.py

Handles persistent memory for the chatbot:
- Saves conversation turns to a local JSON file so the bot remembers
  past sessions, not just the current one.
- Once the raw history grows past a threshold, it asks the model to
  compress older turns into a short summary, keeping the memory file
  small while retaining long-term context.
"""

import json
import os


class MemoryManager:
    def __init__(self, filepath: str, model=None, max_turns: int = 20):
        self.filepath = filepath
        self.model = model
        self.max_turns = max_turns
        self.summary: str = ""
        self.turns: list[dict] = []  # [{"user": ..., "bot": ..., "timestamp": ...}, ...]
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.summary = data.get("summary", "")
                self.turns = data.get("turns", [])
            except (json.JSONDecodeError, OSError):
                # Corrupt or unreadable file — start fresh rather than crash
                self.summary = ""
                self.turns = []

    def save(self):
        data = {"summary": self.summary, "turns": self.turns}
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def clear(self):
        self.summary = ""
        self.turns = []
        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    # ------------------------------------------------------------------
    # Adding + retrieving turns
    # ------------------------------------------------------------------
    def add_turn(self, user_msg: str, bot_msg: str, timestamp: str = ""):
        self.turns.append({"user": user_msg, "bot": bot_msg, "timestamp": timestamp})

    def to_gemini_history(self):
        """
        Build the initial history list passed to model.start_chat().
        Prior long-term summary (if any) is injected as a fake first
        exchange so the model has that context from turn one.
        """
        history = []
        if self.summary:
            history.append({
                "role": "user",
                "parts": [f"(Context from earlier conversations, for your reference only): {self.summary}"],
            })
            history.append({
                "role": "model",
                "parts": ["Understood, I'll keep that in mind."],
            })
        for turn in self.turns:
            history.append({"role": "user", "parts": [turn["user"]]})
            history.append({"role": "model", "parts": [turn["bot"]]})
        return history

    # ------------------------------------------------------------------
    # Summarization (keeps the memory file from growing unbounded)
    # ------------------------------------------------------------------
    def maybe_summarize(self):
        if len(self.turns) < self.max_turns or self.model is None:
            return

        # Summarize everything except the most recent few turns, so
        # recent context stays verbatim and only older stuff gets compressed.
        keep_recent = 5
        to_summarize = self.turns[:-keep_recent]
        remaining = self.turns[-keep_recent:]

        if not to_summarize:
            return

        conversation_text = "\n".join(
            f"User: {t['user']}\nBot: {t['bot']}" for t in to_summarize
        )
        prompt = (
            "Summarize the key facts, preferences, and context from this "
            "conversation history in a few concise bullet points, for use "
            "as long-term memory in future conversations. Be brief and factual:\n\n"
            f"{conversation_text}"
        )
        if self.summary:
            prompt = f"Existing memory summary:\n{self.summary}\n\nNew conversation to fold in:\n\n{prompt}"

        try:
            result = self.model.generate_content(prompt)
            self.summary = result.text.strip()
            self.turns = remaining
        except Exception:
            # If summarization fails, just keep the raw history —
            # it's not worth crashing the chatbot over.
            pass
