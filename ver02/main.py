import logging
import json
import re

import telebot as tlb
from telebot import logger, types

from bdtbs import ids, olympiads, topics, years

# USE "source ~/venv/bin/activate"

# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("bot.log", mode="a", encoding="utf-8")],
)
logger.setLevel(logging.DEBUG)

# -----------------------------
# Bot & Runtime State
# -----------------------------

bot = tlb.TeleBot(ids["bot_api"])  # API token from bdtbs.py
user_data: dict[int, dict] = {}
user_feedback_data: dict[int, dict] = {}

# -----------------------------
# Utilities
# -----------------------------

def bool_has_digit(s):
    """Returns true if there are digits in a string.
    Argument: s (string).
    """
    return bool(re.search(r"\d", s))


def bool_has_ascii_letter(s):
    """Returns true if there are ascii letters in a string.
    Argument: s (string).
    """
    return bool(re.search(r"[A-Za-z]", s))


def bool_has_special_or_nonascii(s):
    """Returns true if there are special or non-ASCII characters.
    Arguments: s (string).
    """
    return bool(re.search(r"[^A-Za-z0-9\s]", s))


def sanitize_numerical_input(user_input: str) -> str:
    """Keeps only digits in a given string."""
    return re.sub(r"[^0-9]", "", user_input)


def sanitize_alphabetical_input(user_input: str) -> str:
    """Keeps only ASCII letters (A-Z, a-z) in a given string."""
    return re.sub(r"[^A-Za-z]", "", user_input)


def _ensure_private(message) -> bool:
    """Reply and abort if chat isn't a private chat."""
    if message.chat.type != "private":
        bot.reply_to(message, "Эта функция доступна только в личных сообщениях боту.")
        return False
    return True


def _kb_with_values(values: list[str], *, include_skip: bool = False, per_row: int = 3) -> types.ReplyKeyboardMarkup:
    """Build a compact keyboard from a list of strings.

    Args:
        values: button labels.
        include_skip: whether to prepend a "skip" button as a separate row.
        per_row: number of buttons per row (best-effort for last row).
    """
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if include_skip:
        kb.add("skip")
    for i in range(0, len(values), per_row):
        kb.row(*values[i : i + per_row])
    return kb



# -----------------------------
# Command Handlers
# -----------------------------



@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.copy_message(message.chat.id, ids["developer_id"], ids["start_fwd_msg_id"])


@bot.message_handler(commands=["id"])
def id_handler(message):
    text = json.dumps(message.json, indent=4, ensure_ascii=False)
    bot.send_message(message.chat.id, f"<pre>{text}</pre>", parse_mode="HTML")


@bot.message_handler(commands=["git"])
def git_handler(message):
    bot.send_message(
        message.chat.id,
        "🔗 Репозиторий: github.com/uhbl/bpsg-telegram-bot\nРазработчик: Абылайхан (github.com/uhbl)",
    )


@bot.message_handler(commands=["cancel"])
def cancel_handler(message):
    user_id = message.chat.id
    if user_id in user_data:
        user_data.pop(user_id)
        bot.send_message(user_id, "🛑 Отправка отменена. Вы можете начать заново с командой /post.")
    else:
        bot.send_message(user_id, "Отменять нечего — активной отправки нет.")


@bot.message_handler(commands=["feedback"])
def feedback_handler(message):
    user_id = message.chat.id
    bot.send_message(user_id, "💬 Оставьте ваш отзыв одним текстовым сообщением — я перешлю его разработчику.")
    user_feedback_data[user_id] = {
        "step": "feedback_called",
        "feedback": None,
        "username": message.from_user.username,
    }


@bot.message_handler(func=lambda m: user_feedback_data.get(m.chat.id, {}).get("step") == "feedback_called")
def feedback_sender(message):
    user_id = message.chat.id
    if len(message.text) < 500:
        user_feedback_data[user_id]["feedback"] = message.text
        bot.send_message(ids["developer_id"], f"#FEEDBACK\n\n'{user_feedback_data[user_id]['feedback']}' from @{user_feedback_data[user_id]['username']}.",)
        user_feedback_data.pop(user_id)
    else:
        bot.send_message(user_id, "Слишком длинное сообщение. Напишите более короткий вариант.")


@bot.message_handler(commands=["post"])
def post_command_handler(message):
    if message.chat.type != "private":
        bot.reply_to(message, "Эта команда доступна только в личных сообщениях боту.")
        return

    user_id = message.chat.id
    user_username = message.from_user.username

    user_data[user_id] = {
        "step": "text",
        "text": None,
        "media_amount": None,
        "media_counter": 0,
        "media_type": None,
        "media": [],
        "media_finished": False,
        "source": None,
        "year": "",
        "topic": None,
        "comments": None,
        "username": user_username,
    }

    bot.send_message(
        user_id,
        "📝 [Шаг 1/7] Текст задачи. Пожалуйста, отправьте формулировку одним сообщением (до 900 символов). Если текст длиннее — в этапе медиа, приложите документом.",
    )


# -----------------------------
# Flow Handlers
# -----------------------------


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "text")
def handle_text(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    if len(message.text) < 900:
        user_data[user_id]["text"] = message.text
        user_data[user_id]["step"] = "media_amount"

        # 0..10 buttons in compact rows
        nums = [str(i) for i in range(0, 11)]
        kb = _kb_with_values(nums, include_skip=False, per_row=4)
        bot.send_message(
            user_id,
            "📎 [Шаг 2/7] Сколько медиа‑файлов вы хотите приложить? Отправьте число 0–10. Нажмите 0, если вложений нет.",
            reply_markup=kb,
        )
    else:
        bot.send_message(
            user_id,
            "⚠️ Текст слишком длинный. Максимальная длина — 900 символов. Вы можете отправить задачу как документ или изображение.",
        )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "media_amount")
def handle_media_amount(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    text = sanitize_numerical_input(message.text)

    if text == "0":
        user_data[user_id]["media_finished"] = True
        user_data[user_id]["step"] = "source"
        bot.send_message(user_id, "Медиа пропущено. Укажите источник задачи.", reply_markup=types.ReplyKeyboardRemove())

        kb = _kb_with_values(list(olympiads.values()), include_skip=True, per_row=3)
        bot.send_message(
            user_id,
            "🎯 [Шаг 3/7] Укажите источник задачи. Пожалуйста, выберите вариант на клавиатуре ниже или нажмите «skip».",
            reply_markup=kb,
        )
        return

    try:
        num = int(text)
        if 1 <= num <= 10:
            user_data[user_id]["media_amount"] = num
            user_data[user_id]["step"] = "media"
            bot.send_message(
                user_id,
                "📤 [Шаг 2/7] Загрузка медиа. Отправьте выбранное количество файлов: только фото ИЛИ только документы.",
                reply_markup=types.ReplyKeyboardRemove(),
            )
        else:
            bot.send_message(user_id, "Допустимо от 1 до 10 файлов. Попробуйте снова.")
    except ValueError:
        bot.send_message(user_id, "Неверный ввод. Отправьте число от 0 до 10.")


@bot.message_handler(content_types=["photo"])
def handle_album_photo(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    if user_data.get(user_id, {}).get("step") != "media":
        return

    if user_data[user_id]["media_type"] is None:
        user_data[user_id]["media_type"] = "photo"
    elif user_data[user_id]["media_type"] != "photo":
        bot.send_message(user_id, "Нельзя смешивать типы: вы уже загружаете документы. Добавление фото отклонено.")
        return

    user_data[user_id]["media_type"] = "photo"
    user_data[user_id]["media"].append(message.photo[-1].file_id)
    user_data[user_id]["media_counter"] += 1

    if user_data[user_id]["media_counter"] == user_data[user_id]["media_amount"]:
        user_data[user_id]["media_finished"] = True
        user_data[user_id]["step"] = "source"
        kb = _kb_with_values(list(olympiads.values()), include_skip=True, per_row=3)
        bot.send_message(
            user_id,
            "✅ Медиа приняты. 🎯 [Шаг 3/7] Укажите источник задачи. Выберите вариант на клавиатуре ниже или нажмите «skip».",
            reply_markup=kb,
        )


@bot.message_handler(content_types=["document"])
def handle_album_document(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    if user_data.get(user_id, {}).get("step") != "media":
        return

    if user_data[user_id]["media_type"] is None:
        user_data[user_id]["media_type"] = "document"
    elif user_data[user_id]["media_type"] != "document":
        bot.send_message(user_id, "Нельзя смешивать типы: вы уже загружаете фото. Добавление документа отклонено.")
        return

    user_data[user_id]["media_type"] = "document"
    user_data[user_id]["media"].append(message.document.file_id)
    user_data[user_id]["media_counter"] += 1

    if user_data[user_id]["media_counter"] == user_data[user_id]["media_amount"]:
        user_data[user_id]["media_finished"] = True
        user_data[user_id]["step"] = "source"
        kb = _kb_with_values(list(olympiads.values()), include_skip=True, per_row=3)
        bot.send_message(
            user_id,
            "✅ Медиа приняты. 🎯 [Шаг 3/7] Укажите источник задачи. Выберите вариант на клавиатуре ниже или нажмите «skip».",
            reply_markup=kb,
        )


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "source")
def handle_source(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    source_olymps = sanitize_alphabetical_input(message.text)

    if source_olymps in olympiads.values():
        user_data[user_id]["source"] = source_olymps
        user_data[user_id]["step"] = "year"
        bot.send_message(
            user_id,
            "📅 [Шаг 4/7] Укажите год в формате YYYY (например, 2025).",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    elif source_olymps == "skip":
        user_data[user_id]["source"] = "Другое"
        user_data[user_id]["step"] = "topic"
        kb = _kb_with_values(list(topics.values()), include_skip=False, per_row=3)
        bot.send_message(
            user_id,
            "Источник пропущен. 📚 [Шаг 5/7] Выберите тему на клавиатуре ниже. Если хотите пропустить — введите «skip».",
            reply_markup=kb,
        )
    else:
        bot.send_message(user_id, "Неверный ввод. Пожалуйста, выберите вариант кнопкой на клавиатуре ниже.")


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "year")
def handle_year(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    clear_year = sanitize_numerical_input(message.text)
    if bool_has_digit(clear_year):
        ymin = years.get("lower_bound", years.get("min", 1990))
        ymax = years.get("upper_bound", years.get("max", 2027))
        if clear_year and clear_year.isdigit() and ymin <= int(yr) <= ymax:
            user_data[user_id]["year"] = clear_year
            user_data[user_id]["step"] = "topic"
            kb = _kb_with_values(list(topics.values()), include_skip=False, per_row=3)
            bot.send_message(user_id, "Год указан. Теперь укажите тему задачи (по гайду).", reply_markup=kb)
        else:
            bot.send_message(user_id, "Укажите правильный год.")
    else:
        bot.send_message(user_id, "Год должен быть указан при помощи цифр (слова не поддерживаются).")


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "topic")
def handle_topic(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    if message.text in topics.values():
        user_data[user_id]["topic"] = message.text
        user_data[user_id]["step"] = "comments"
        bot.send_message(user_id, "📝 [Шаг 6/7] Добавьте комментарии (по желанию). Если их нет — напишите «нет».")
    else:
        bot.send_message(user_id, "Неверный ввод. Пожалуйста, выберите тему кнопкой на клавиатуре ниже.")


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "comments")
def handle_comments(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    if len(message.text) < 100:
        user_data[user_id]["comments"] = message.text
        bot.send_message(user_id, "🔍 [Шаг 7/7] Формирую предпросмотр… Это займёт несколько секунд.")
        preview_problem(user_id)
        user_data[user_id]["step"] = "preview_confirm"
    else:
        bot.send_message(user_id, "Комментарии слишком большой. Сделайте его короче 100 символов пожалуйста.")


# -----------------------------
# Preview & Send
# -----------------------------

def preview_problem(user_id: int) -> None:
    data = user_data[user_id]
    formatted_message = (
        f"Source: #{data['source']}{data['year']}\n"
        f"Topic: #{data['topic']}\n\n{data['text']}\n\nКомментарии: {data['comments']}"
    )

    media_type = data["media_type"]
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("Yes", "No")

    if media_type == "photo":
        media = [types.InputMediaPhoto(media=file_id) for file_id in data["media"]]
        media[0].caption = formatted_message
        bot.send_media_group(user_id, media=media)
    elif media_type == "document":
        media = [types.InputMediaDocument(media=file_id) for file_id in data["media"]]
        media[-1].caption = formatted_message
        bot.send_media_group(user_id, media=media)
    else:
        bot.send_message(user_id, formatted_message)

    bot.send_message(user_id, "✅ Всё выглядит корректно? Отправить задачу администраторам? (Yes/No)", reply_markup=kb)


@bot.message_handler(func=lambda m: user_data.get(m.chat.id, {}).get("step") == "preview_confirm")
def handle_preview_confirmation(message):
    if not _ensure_private(message):
        return

    user_id = message.chat.id
    text = message.text.strip().lower()
    if text == "yes":
        send_problem(user_id)
        bot.send_message(user_id, "🎉 Готово! Задача отправлена администраторам. Спасибо!", reply_markup=types.ReplyKeyboardRemove())
    elif text == "no":
        user_data.pop(user_id)
        bot.send_message(user_id, "Отправка отменена. Вы можете начать заново с /post.", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(user_id, "Пожалуйста, нажмите кнопку «Yes» или «No».")


def send_problem(user_id: int) -> None:
    data = user_data[user_id]
    formatted_message = (
        f"Source: #{data['source']}{data['year']}\n"
        f"Topic: #{data['topic']}\n\n{data['text']}\n\nКомментарии: {data['comments']}"
    )

    media_type = data["media_type"]
    if media_type == "photo":
        media = [types.InputMediaPhoto(media=file_id) for file_id in data["media"]]
        media[0].caption = formatted_message
        bot.send_media_group(ids["problems_id"], media=media)
    elif media_type == "document":
        media = [types.InputMediaDocument(media=file_id) for file_id in data["media"]]
        media[-1].caption = formatted_message
        bot.send_media_group(ids["problems_id"], media=media)
    else:
        bot.send_message(ids["problems_id"], formatted_message)

    bot.send_message(ids["problems_id"], f"ID: {user_id}\n@: @{data['username']} \n")
    user_data.pop(user_id)


# -----------------------------
# Polling
# -----------------------------
bot.infinity_polling()
