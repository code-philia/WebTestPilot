Automators are browser automation drivers that translate the output of LLM agents into executable actions that interact with the current webpage.

Each driver maps a specific action space into Playwright commands (or other automation backends).

Available drivers:

- `custom.py` – Maps a custom Python function–based action space to Playwright actions (e.g., GPT, Claude, Gemini, Qwen, ...).
- `uitars.py` – Maps the UI-TARS supported action space to Playwright actions (e.g., UI-TARS).
- `pyautogui.py` – Maps the PyAutoGUI action space for desktop-level interactions (e.g., InternVL3).