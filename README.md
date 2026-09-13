# Custom AI Chatbot with Memory

A simple command-line AI chatbot built in Python, powered by the Gemini API
(from Google AI Studio), with persistent memory across sessions.

## Features

- Chats using Google's Gemini model via the official `google-generativeai` SDK
- **Persistent memory**: conversations are saved to `memory.json`, so the bot
  remembers you the next time you run it
- **Auto-summarization**: once the conversation history gets long, older
  turns are compressed into a short summary (via the model itself) so memory
  doesn't grow forever or blow past context limits
- `forget` command to wipe memory and start clean

## 1. Get an API key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in and click **Create API key**
3. Copy the key — you'll need it in step 3 below

## 2. Set up the project in VS Code

1. Open this folder in VS Code (`File > Open Folder...`)
2. Open a terminal in VS Code (`` Ctrl+` `` / `` Cmd+` ``)
3. Create a virtual environment (recommended):

   ```bash
   python -m venv venv
   ```

   Activate it:
   - **Windows**:venv\Scripts\activate
   - **Mac/Linux**: `source venv/bin/activate`

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## 3. Add your API key

Copy `.env.example` to a new file named `.env`, and paste your key in:

```bash
cp .env.example .env
```

Then edit `.env` so it looks like:

```
GEMINI_API_KEY=AIzaSy...your_actual_key...
```

`.env` is read automatically by the script — never commit it or share it publicly.

## 4. Run it

```bash
python chatbot.py
```

Example session:

```
You: Hi, I'm learning Python and I love hiking.
Bot: Nice to meet you! ...

You: exit
```

Run it again later — the bot will still remember what you told it, because
it's saved in `memory.json`.

### Commands
- `exit` / `quit` — end the session
- `forget` — permanently wipe all stored memory

## How the memory works

- Every user/bot exchange is appended to `memory.json`.
- On startup, that history (plus any long-term summary) is loaded back in
  as the starting context for the chat.
- Once the raw history passes a threshold (default: 20 turns), the oldest
  turns are summarized by the model into a few bullet points and replaced
  with that summary — keeping the file small while preserving long-term
  context. You can tune this via `MAX_TURNS_BEFORE_SUMMARY` in `chatbot.py`.

## Customizing

- **Change the model**: edit `MODEL_NAME` in `chatbot.py` (e.g. to
  `gemini-2.0-pro` or a newer model, once available — check
  [Google AI Studio](https://aistudio.google.com) for current model names).
- **Change the personality**: edit `SYSTEM_PROMPT` in `chatbot.py`.
- **Change how much history is kept before summarizing**: edit
  `MAX_TURNS_BEFORE_SUMMARY`.

## Project structure

```
gemini_chatbot/
├── chatbot.py          # main CLI loop
├── memory_manager.py   # persistent memory + summarization logic
├── requirements.txt
├── .env.example
├── memory.json          # created automatically after your first chat
└── README.md
```
