# BioProblemSolving Telegram Bot

_Warning:_ USE "source ~/venv/bin/activate" each time when executing bot script in environments like RAPSI.

This is the first version of a Telegram bot for the **BioProblemSolving** community.  
It helps users submit biology Olympiad-style problems and questions into the moderation queue before being published in the official channel.

---

## Features

- **/start** → Welcomes the user, explains available commands.  
- **/guide** → Provides detailed instructions and formatting rules for posting tasks.  
- **/post** → Interactive, step-by-step submission:
  1. Enter the problem text.  
  2. (Optional) Upload an image (PNG/JPG/JPEG, also supported as a file).  
  3. Specify the **source** of the task (Olympiad, exam, textbook, etc. using short tags).  
  4. Specify the **topic** (e.g., genetics, botany, physiology).  
  5. Add optional comments.  

Each submission is forwarded to admins for review before publication.

---

## Technical Details

- Built with [PyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (`telebot`).
- Stores temporary user submission data in memory (`user_data` dictionary).
- Logs all user interactions and commands to a separate log chat.
- Supports both **photo messages** and **file uploads** for task images.

---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/uhbl/bpsg-telegram-bot
cd ~/bpsg-telegram-bot
```

2. Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure your bot:

- Get a bot token from @BotFather
- Replace 'API' in bot_ver01.py with your token.
- Replace probs_id and logs_id with the chat IDs for the problem channel and logs channel.

4. Run the bot:

```bash
python bot_ver01.py
```

---

**Usage Example**
    User runs /post.
    Bot asks for problem text → user provides it.
    Bot asks for image → user uploads or types skip.
    Bot asks for source → user enters e.g. ibo_2015.
    Bot asks for topic → user enters e.g. genetics.
    Bot asks for comments → user writes or types нет.
    Bot forwards the fully assembled task to moderators.

---

**Contribution**

This project is in early development. Future improvements may include:
    More commands and functionality.
    Automatic tagging and formatting.
    Database-backed storage instead of in-memory.
    Feel free to fork and contribute!

---

**LICENSE**

MIT License.