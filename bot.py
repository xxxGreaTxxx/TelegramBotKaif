import telebot
import os

TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    raise Exception("Не задана переменная окружения с токеном бота")

bot = telebot.TeleBot(TOKEN)

user_states = {}

# Путь к файлу для сохранения информации о пользователях
USERS_FILE = 'users.txt'

# Функция сохранения информации о пользователе в файл
ADMIN_CHAT_ID = ['204467798']


def save_user_info(user):
    with open(USERS_FILE, 'a') as file:
        file.write(
            f"{user.id},{user.first_name},{user.last_name},{user.username}\n")


def check_user_in_file(user):
    with open(USERS_FILE, 'r') as file:
        lines = file.readlines()
        for line in lines:
            user_id = int(line.split(sep=',')[0])
            if user_id == user.id:
                print("Пользователь уже подписан")
                return True
        return False


@bot.message_handler(commands=['start'])
def start_handler(message):
    if not check_user_in_file(message.from_user):
        save_user_info(message.from_user)
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user_full_name = message.from_user.full_name
    username = message.from_user.username

    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('Записаться')
    itembtn2 = telebot.types.KeyboardButton('Написать сообщение')
    markup.add(itembtn1, itembtn2)

    msgHi = f'Привет, {user_full_name}, пришло время присоединиться к кайфожорам. С нами весело! ;) \n\nТы можешь написать в чат сообщение и мы на него ответим, либо записаться на наши мероприятия'

    bot.send_message(user_id, msgHi, reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == 'Записаться')
def send_registration(message):
    # Отправляем сообщение с просьбой о заполнении данных
    user_states[message.chat.id] = 'registration'
    bot.send_message(message.from_user.id,
                     "Пожалуйста, напиши на какое мероприятие ты хочешь записаться?")

# Обработчик нажатия кнопки "Написать сообщение"


@bot.message_handler(func=lambda message: message.text == 'Написать сообщение')
def send_message(message):
    # Отправляем сообщение с просьбой о написании сообщения
    user_states[message.chat.id] = 'message'
    bot.send_message(message.from_user.id, "Напиши свое сообщение.")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    state = user_states.get(message.chat.id)

    if state == 'registration':
        # Отправляем данные администратору
        # admin_chat_id = '204467798'
        admin_message = f"Пользователь {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username}) хочет записаться.\n\nДанные мероприятия:\n{message.text}"
        for id in ADMIN_CHAT_ID:
            # bot.send_message(admin_chat_id, admin_message)
            bot.send_message(id, admin_message)
        # Отправляем подтверждение пользователю
        bot.send_message(message.from_user.id, "Спасибо! Будем тебя ждать!")

    elif state == 'message':
        # Отправляем сообщение администратору
        # admin_chat_id = '204467798'
        admin_message = f"Пользователь {message.from_user.first_name} {message.from_user.last_name} (@{message.from_user.username}) отправил сообщение:\n\n{message.text}"
        for id in ADMIN_CHAT_ID:
            # bot.send_message(admin_chat_id, admin_message)
            bot.send_message(id, admin_message)

        # Отправляем подтверждение пользователю
        bot.send_message(message.from_user.id,
                         "Спасибо! Мы скоро тебе ответим.")

    else:
        bot.send_message(message.from_user.id,
                         'Извините, я не понимаю, что ты хочешь сделать :(')

    user_states.pop(message.chat.id, None)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
