import telebot as tlb
from telebot import types
from datetime import datetime

# API and ID are subject to change in case of use. Please, use /id command to view all the .json data about the chat.
bot = tlb.TeleBot('API')
probs_id = "ID_1"
logs_id = "ID_2"
test_id = "ID_3"
dev_id = "ID_4"
forward_message_id = "ID_5"
user_data = {}
user_feedback_data = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.copy_message(message.chat.id, dev_id, forward_message_id)

@bot.message_handler(commands=['id'])
def id_handler(message):
    bot.send_message(message.chat.id, message.json)

@bot.message_handler(commands=['cancel'])
def cancel_handler(message):
    user_id = message.chat.id
    if user_id in user_data:
        user_data.pop(user_id)
        bot.send_message(user_id, "Your submission has been canceled. You can start over with /post.")
    else:
        bot.send_message(user_id, "There's nothing to cancel.")

@bot.message_handler(commands=['feedback'])
def feedback_handler(message):
    user_id = message.chat.id
    bot.send_message(user_id, "Напишите ваш фидбэк в виде текста. Фидбек будет отправлен разработчику бота.")
    user_feedback_data[user_id] = {
        "step": "feedback_called",
        "feedback": None,
        "username": message.from_user.username
    }

@bot.message_handler(func=lambda message: user_feedback_data.get(message.chat.id, {}).get("step") == "feedback_called")
def feedback_sender(message):
    user_id = message.chat.id
    user_feedback_data[user_id]["feedback"] = message.text
    bot.send_message(dev_id, f"'{user_feedback_data[user_id]["feedback"]}' from @{user_feedback_data[user_id]["username"]} at {datetime.now()}.")

@bot.message_handler(commands=['post'])
def post_command_handler(message):
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
        "topic": None, 
        "comments": None, 
        "username": user_username,
    }
    bot.send_message(user_id, "Пожалуйста, напишите условия вашей задачи.")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "text")
def handle_text(message):
    user_id = message.chat.id
    user_data[user_id]["text"] = message.text
    user_data[user_id]["step"] = "media_amount"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("skip", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10")
    bot.send_message(user_id, "Сколько медиа-файлов (фото или документов)? Напишите только число. Если же ничего нет, нажмите на кнопку skip.", reply_markup=markup)

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "media_amount")
def handle_media_amount(message):
    user_id = message.chat.id
    text = message.text.strip().lower()
    if text == "skip" or "0":
        user_data[user_id]["media_finished"] = True
        user_data[user_id]["step"] = "source"
        bot.send_message(user_id, "Медиа пропущено. Укажите источник задачи.", reply_markup=types.ReplyKeyboardRemove())
        return
    try:
        num = int(text)
        if 1 <= num <= 10:
            user_data[user_id]["media_amount"] = num
            user_data[user_id]["step"] = "media"
            bot.send_message(user_id, "Теперь отправьте медиа-файлы (фото или документы).", reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(user_id, "Разрешено от 1 до 10 медиа-файлов. Попробуйте снова.")
    except ValueError:
        bot.send_message(user_id, "Неверный ввод. Введите число (1–10) или 'skip'.")

@bot.message_handler(content_types=['photo'])
def handle_album_photo(message):
    user_id = message.chat.id
    if user_data.get(user_id, {}).get("step") == "media":
        user_data[user_id]["media_type"] = "photo"
        user_data[user_id]["media"].append(message.photo[-1].file_id)
        user_data[user_id]["media_counter"] += 1
        if user_data[user_id]["media_counter"] == user_data[user_id]["media_amount"]:
            user_data[user_id]["media_finished"] = True
            user_data[user_id]["step"] = "source"
            bot.send_message(user_id, "Медиа-файлы приняты. Теперь укажите источник задачи.")

@bot.message_handler(content_types=['document'])
def handle_album_document(message):
    user_id = message.chat.id
    if user_data.get(user_id, {}).get("step") == "media":
        user_data[user_id]["media_type"] = "document"
        user_data[user_id]["media"].append(message.document.file_id)
        user_data[user_id]["media_counter"] += 1
        if user_data[user_id]["media_counter"] == user_data[user_id]["media_amount"]:
            user_data[user_id]["media_finished"] = True
            user_data[user_id]["step"] = "source"
            bot.send_message(user_id, "Медиа-файлы приняты. Теперь укажите источник задачи.")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "source")
def handle_source(message):
    user_id = message.chat.id
    user_data[user_id]["source"] = message.text
    user_data[user_id]["step"] = "topic"
    bot.send_message(user_id, "Теперь укажите тему задачи (по гайду).")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "topic")
def handle_topic(message):
    user_id = message.chat.id
    user_data[user_id]["topic"] = message.text
    user_data[user_id]["step"] = "comments"
    bot.send_message(user_id, "Оставьте комментарии, если есть. Напишите 'нет', если их нет.")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "comments")
def handle_comments(message):
    user_id = message.chat.id
    user_data[user_id]["comments"] = message.text
    bot.send_message(user_id, "Осмотрите вашу задачу напоследок перед отправкой. Это может занять пару секунд.")
    preview_problem(user_id)
    user_data[user_id]["step"] = "preview_confirm"

def preview_problem(user_id):
    data = user_data[user_id]
    formatted_message = (f"#источник_{data['source']}\n#тема_{data['topic']}\n\n{data['text']}\n\nКомментарии: {data['comments']}")
    media_type = data["media_type"]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Yes", "No")
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
    bot.send_message(user_id, "Вы хотите отправить задачу администраторам?", reply_markup=markup)

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "preview_confirm")
def handle_preview_confirmation(message):
    user_id = message.chat.id
    text = message.text.strip().lower()
    if text == "yes":
        send_problem(user_id)
        bot.send_message(user_id, "Ваша задача была переслана админам. Спасибо!", reply_markup=types.ReplyKeyboardRemove())
    elif text == "no":
        user_data.pop(user_id)
        bot.send_message(user_id, "Отправка отменена. Вы можете начать заново с помощью /post.", reply_markup=types.ReplyKeyboardRemove())
    else:
        bot.send_message(user_id, "Пожалуйста, нажмите 'Yes' или 'No'.")

def send_problem(user_id):
    data = user_data[user_id]
    formatted_message = (f"#источник_{data['source']}\n#тема_{data['topic']}\n\n{data['text']}\n\nКомментарии: {data['comments']}")
    media_type = data["media_type"]
    if media_type == "photo":
        media = [types.InputMediaPhoto(media=file_id) for file_id in data["media"]]
        media[0].caption = formatted_message
        bot.send_media_group(test_id, media=media)
    elif media_type == "document":
        media = [types.InputMediaDocument(media=file_id) for file_id in data["media"]]
        media[-1].caption = formatted_message
        bot.send_media_group(test_id, media=media)
    else:
        bot.send_message(test_id, formatted_message)
    bot.send_message(test_id, f"Date(UTC): {datetime.now()}\nID: {user_id}\n@: @{data['username']} \n")
    user_data.pop(user_id)

bot.polling(none_stop=True)