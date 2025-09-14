import telebot as tlb
from datetime import datetime

# API and ID are subject to change. In case of use, please identify your API via @BotFather and ID by devtools of tg.
bot = tlb.TeleBot('API')
probs_id = ID
logs_id = ID
user_data = {}

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, 
    f"Привет, {message.from_user.first_name}! \n \n" 
    "Добро пожаловать в бот который поможет вам загрузить ваши вопросы касательно олимпиадной биологии "
    "в канал BioProblemSolving. " 
    "В особенности олимпиадные задачи! \n \n"
    "Прежде чем начнёте пользоваться данным ботом, вам стоит ознакомится с основными правилами в гайде. \n \n"
    "Команды: \n/start - команда, предназначенная для активации бота и выдачи всех команд (всё это сообщение).\n"
    "/guide - команда, которая выдает инструкции о пользовании ботом. Рекоммендуем прочитать. \n"
    "/post - команда, которая непосредственно нужна для публикации вашей задачи или вопроса. \n \n"
    "(Бот находится в разработке, поэтому в будущем постараемся внедрить больше команд и "
    "оптимизировать работу бота.) \n \n"
    "Если ознакомились с командами, то можете продолжить к прочтению гайда и отправке вашей задачи."
    )
    bot.send_message(logs_id, 
        f"Date : {datetime.now()} <The time is in UTC. KZ is in UTC+5.>\n"
        "Command : /start \n"
        f"Telegram ID : {message.chat.id} \n"
        f"Username : {message.from_user.username} \n"
    )

@bot.message_handler(commands=['guide'])
def guide_handler(message):
    bot.send_message(message.chat.id,
        "<b><u>Что делает данный бот?</u></b>\n\n"
        "Бот нужен для того чтобы вы могли публиковать ваши вопросы касательно олимпиадной биологи и задачи в канал BioProblemSolving. \n\n"
        "<b><u>Как публикуется ваш вопрос/задача?</u></b>\n\n"
        "Каждый пост проходит модерацию. То есть бот переправляет вопросы/задачи модераторам, которые публикуют ваш пост в канал. Однако стоит учитывать что если "
        "вы отправите вопрос поздно ночью, то он скорее всего опубликуется только на завтрашний день. \n\n"
        "<b><u>Как им 'правильно' пользоваться?</u></b>\n\n"
        "Через команду /post вы можете отправлять ваши вопросы и задачи на который хотите ответ. "
        "Данная команда предоставляет возможность 'создавать' ваш вопрос пошагово, что облегчает работу вам и модераторам канала "
        "BioProblemSolving. Есть определенные моменты которых надо избегать.\n\n"
        "<b><u>1.</u></b> После отправки команды /post боту, пожалуйста, не оставляйте бота без ответа. Ему будет обидно за игнор :(. "
        "Если серьезно, то это немного ухудшает работу бота.\n"
        "<b><u>2.</u></b> Не добавляйте бота в группы или каналы. Бот предназначен для индивидуального пользования.\n"
        "<b><u>3.</u></b> Не отправляйте команды просто так или без особых причин. Это просто так использует ресурс бота.\n"
        "<b><u>4.</u></b> Важный момент. Для упрощения использования функции поиска внутри канала по источникам и темам, "
        "вы должны будете отправлять их боту в специальном формате: \n\n"
        "   1. Для источников которые являются олимпиадой или экзаменом, формат таков: {укороченное название олимпиады или экзамена}_{год проведения}. "
        "Например: респа_2019, область_2022, ibo_2015.\n"
        "   2. Для источников которые являются книгой или сборником задач, формат таков: {распространенное короткое название}_{номер главы}. "
        "Например: кэмпбелл_44, каммингс_5, ленинджер_3, шаумс_6.\n"
        "   3. Для тем, формат таков: {распространенное короткое название темы}. "
        "Например: генетика, молекулярка, ботаника, анат_и_физ_животных, биосистематика.\n\n"
        "<i><b>Желаем вам приятной работы с ботом!</b></i>",
        parse_mode='html'
    )
    bot.send_message(
        logs_id, 
        f"Date : {datetime.now()} <The time is in UTC. KZ is in UTC+5.>\n"
        "Command : /guide \n"
        f"Telegram ID : {message.chat.id} \n"
        f"Username : {message.from_user.username} \n"
    )

@bot.message_handler(commands=['post'])
def post_command_handler(message):
    user_id = message.chat.id
    user_username = message.from_user.username
    user_data[user_id] = {
        "step": "text",
        "text": None,
        "image": None,
        "source": None,
        "topic": None,
        "comments": None,
        "username": user_username,
    }
    bot.send_message(user_id, "Пожалуйста, напишите условия вашей задачи.")
    bot.send_message(logs_id, 
        f"Date : {datetime.now()} <The time is in UTC. KZ is in UTC+5.>\n"
        "Command : /post \n"
        f"Telegram ID : {message.chat.id} \n"
        f"Username : {message.from_user.username} \n"
    )

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "text")
def handle_text(message):
    user_id = message.chat.id
    user_data[user_id]["text"] = message.text
    user_data[user_id]["step"] = "image"
    bot.send_message(user_id, 
        "Далее, пожалуйста, предоставьте фото для вашей задачи если нужно (если в виде файла, то только в формате .png или .jpg/.jpeg).\n\n"
        "Если фото к данной задаче не нужна, напишите 'skip'.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.chat.id
    if user_data.get(user_id, {}).get("step") == "image":
        try:
            file_id = message.photo[-1].file_id
            user_data[user_id]["image"] = file_id
            user_data[user_id]["step"] = "source"
            bot.send_message(user_id, "Фото было принято успешно!")
            bot.send_message(user_id, "Далее, назовите источник с которого была взята задача (ссылайтесь на гайд).")
        except (IndexError, AttributeError):
            bot.send_message(user_id, "Возникла проблема при обработке запроса. Попробуйте снова!")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.chat.id
    if user_data.get(user_id, {}).get("step") == "image":
        try:
            file_name = message.document.file_name
            if file_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_id = message.document.file_id
                user_data[user_id]["image"] = file_id
                user_data[user_id]["step"] = "source"
                bot.send_message(user_id, "Фото (как файл) было принято успешно!")
                bot.send_message(user_id, "Далее, назовите источник с которого была взята задача (ссылайтесь на гайд).")
            else:
                bot.send_message(user_id, "Файл, который вы отправили не является нужного формата. Пожалуйста пришлите файл в формате .png, .jpg, или .jpeg.")
        except AttributeError:
            bot.send_message(user_id, "Возникла проблема при обработке запроса. Попробуйте снова!")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "image")
def handle_image_skip(message):
    if message.text.lower() == "skip" or "скип":
        user_id = message.chat.id
        user_data[user_id]["step"] = "source"
        bot.send_message(user_id, "Окей.")
        bot.send_message(user_id, "Далее, назовите источник с которого была взята задача (ссылайтесь на гайд).")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "source")
def handle_source(message):
    user_id = message.chat.id
    user_data[user_id]["source"] = message.text
    user_data[user_id]["step"] = "topic"
    bot.send_message(user_id, "Далее, назовите тему данной задачи (ссылайтесь на гайд).")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "topic")
def handle_topic(message):
    user_id = message.chat.id
    user_data[user_id]["topic"] = message.text
    user_data[user_id]["step"] = "comments"
    bot.send_message(user_id, "Напоследок, можете оставить комментарии если имеются. Напишите нет если нет никаких комментарии.")

@bot.message_handler(func=lambda message: user_data.get(message.chat.id, {}).get("step") == "comments")
def handle_comments(message):
    user_id = message.chat.id
    user_data[user_id]["comments"] = message.text
    assemble_and_send_to_admin(user_id)
    bot.send_message(user_id, "Ваша задача была переслана админам. Спасибо!")

def assemble_and_send_to_admin(user_id):
    data = user_data[user_id]
    formatted_message = (
        f"#источник_{data['source']}\n"
        f"#тема_{data['topic']}\n\n"
        f"{data['text']}\n\n"
        f"Комментарии: {data['comments']}"
    )
    username = data["username"]
    if data["image"]:
        try:
            bot.send_photo(probs_id, data["image"], caption=formatted_message)
        except Exception as e:
            bot.send_document(probs_id, data["image"], caption=formatted_message)
    else:
        bot.send_message(probs_id, formatted_message)
    bot.send_message(logs_id, 
        f"Date : {datetime.now()} <The time is in UTC. KZ is in UTC+5.>\n"
        "Type : Задача/Вопрос \n"
        f"Telegram ID : {user_id} \n"
        f"Username : {username} \n"
    )

bot.polling(none_stop=True)