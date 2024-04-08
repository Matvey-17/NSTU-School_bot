import telebot

from models import (add_student, set_curator, add_curator,
                    set_active, list_students, complete, add_chat_id,
                    set_chat_id, add_one_message, set_one_message)
from config import TOKEN

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    if message.from_user.id == 777759367:
        add_curator(message.from_user.id)

        bot.delete_message(message.chat.id, message.id)

        bot.send_message(message.chat.id,
                         'Привет, куратор 👋\n\n<b>Доступные команды:</b>\n!вход - Выход <b>на смену</b> в чат\n'
                         '!выход - Выход <b>со смены</b>\n!студенты - Список студентов, которым '
                         '<b>необходимо ответить</b>\n'
                         '!завершить id - Завершить диалог со студентом '
                         '(на месте <b>id</b> должен быть <b>id студента</b>)',
                         parse_mode='html')
    else:
        add_student(message.from_user.id, message.from_user.username)

        bot.delete_message(message.chat.id, message.id)

        markup = telebot.types.InlineKeyboardMarkup()
        btn_questions = telebot.types.InlineKeyboardButton('Задать вопрос', callback_data='questions')
        markup.add(btn_questions)

        bot.send_message(message.chat.id,
                         'Привет, дорогой студент 🎓 Добро пожаловать в <b>онлайн-куратор NSTU_School</b>! '
                         'Здесь ты сможешь задать вопросы наставнику по темам курса, если возникнут трудности с '
                         'пониманием какой-либо темы ❓', reply_markup=markup, parse_mode='html')


@bot.callback_query_handler(func=lambda call: call.data == 'questions')
def questions(callback: telebot.types.CallbackQuery):
    bot.send_message(callback.message.chat.id,
                     'Ниже ты можешь задать свой вопрос 👇\n\nНапример: "Здравствуйте! У меня '
                     'не получается разобраться с производной от неявно заданной функции. '
                     'Прочитал теорию, посмотрел примеры, но когда начинаю самостоятельно '
                     'решать задачи, то допускаю ошибки. Помогите, пожалуйста, разобраться"'
                     '\n\nP.S. Мы отвечаем на вопросы по темам <b>наших курсов</b> 🥺', parse_mode='html')


@bot.message_handler(
    func=lambda message: message.chat.type == 'supergroup' and message.from_user.first_name == 'Telegram')
def msg_supergroup(message):
    text_new = (message.text.split('-'))[0]
    res_new_2_new = add_chat_id(text_new, message.message_id)
    message_text = set_one_message(text_new)
    bot.send_message(-1002073307779, f'{message_text}', reply_to_message_id=res_new_2_new)


@bot.message_handler(func=lambda message: True)
def msg_questions(message: telebot.types.Message):
    if message.chat.type == 'private' and message.from_user.id != 777759367:
        add_one_message(message.from_user.id, message.text)
        res_new = set_chat_id(message.from_user.id)
        if res_new[0] == False:
            bot.send_message(-1002136452669, f'{message.from_user.id} - {message.from_user.username}')
        else:
            bot.send_message(-1002073307779, f'{message.text}', reply_to_message_id=int(res_new[1]))

        res = set_curator(message.from_user.id)
        if res[0] == 1:
            bot.send_message(message.chat.id,
                             'Принято ✅\nТвой вопрос перенаправлен наставнику. В течение 5-7 минут он с тобой '
                             'свяжется и поможет тебе ⏳')
            bot.send_message(res[1], 'У тебя новый ученик 🆕\n\n'
                                     f'🌀 Имя пользователя - @{message.from_user.username}\n'
                                     f'❓ Вопрос: {message.text}')
        elif res[0] == -1:
            bot.send_message(message.chat.id, 'К сожалению, в данный момент чат закрыт, приходи чуть позже 🔒')
        else:
            pass
    elif message.from_user.id == 777759367 and message.chat.type == 'private':
        if message.text == '!вход':
            set_active(message.from_user.id, 1)
            bot.send_message(message.chat.id, 'Удачи на смене 🍀')
        elif message.text == '!выход':
            set_active(message.from_user.id, 0)
            bot.send_message(message.chat.id, 'Спасибо, твоя смена завершена! Ждем возвращения 🕙')
        elif message.text == '!студенты':
            res = list_students(message.from_user.id)
            bot.send_message(message.chat.id, res)
        elif message.text.startswith('!завершить') and len(message.text) >= 12:
            if message.text[10] == ' ' and message.text[11] != ' ':
                command = message.text.split(' ')
                if command[1].isdigit():
                    tg_id = command[1]
                    res = complete(tg_id)
                    if res[0] == 1:
                        bot.send_message(message.chat.id, f'Диалог с @{res[1]} завершен ')
                    else:
                        bot.send_message(message.chat.id, 'Пользователь не найден ❌')
                else:
                    bot.send_message(message.chat.id, 'Что-то пошло не так, проверь корректность данных ❌')
            else:
                bot.send_message(message.chat.id, 'Что-то пошло не так, проверь корректность данных ❌')
        else:
            bot.send_message(message.chat.id, 'Неверная команда ❌')


if __name__ == "__main__":
    bot.infinity_polling(skip_pending=True)
