from functools import wraps
import telegram
from telegram import Update, ReplyKeyboardMarkup, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

import config
from db_manager import DB_manager
from services.mail_traking_notifycations import short_report, full_report

db_manager = DB_manager()
bot = telegram.Bot(token=config.TOKEN)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)

    return command_func







@send_typing_action
def StartHandler(update: Update, context: CallbackContext):
    # b.write_user_position(update.message.chat_id, "main")

    print(f"New message from {update.message.chat_id} , text : {update.message.text}")


    user_id = update.message.from_user.id
    if not db_manager.user_exist(user_id): db_manager.add_user(user_id)
    db_manager.update_user_position(user_id, "StartHandler")
    db_manager.debug_info()

    keyboard = [
        [telegram.KeyboardButton("Добавить отправление ➕")],
        [telegram.KeyboardButton("Мои отправления ✉")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text('Пожалуйста выберете!', reply_markup=reply_markup)

@send_typing_action
def AddDeparture(update: Update, context: CallbackContext):
    # b.write_user_position(update.message.chat_id, "main")
    print(f"New message from {update.message.chat_id} , text : {update.message.text}")


    user_id = update.message.from_user.id
    db_manager.update_user_position(user_id, "AddDeparture")
    db_manager.debug_info()

    keyboard = [
        [telegram.KeyboardButton("Назад ◀️")],
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text("Трек номер:", reply_markup=reply_markup)

@send_typing_action
def MyDepartures(update: Update, context: CallbackContext):
    print(f"New message from {update.message.chat_id} , text : {update.message.text}")


    user_id = update.message.from_user.id
    db_manager.update_user_position(user_id, "MyDepartures")
    db_manager.debug_info()

    keyboard = [
        [telegram.KeyboardButton("Назад ◀️")],
    ]

    if len(db_manager.get_user_departures(user_id)) == 0:
        departures = "Нет отправлений"
    else:
        departures = db_manager.get_user_departures(user_id)

    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text(departures, reply_markup=reply_markup)

@send_typing_action
def Other(update: Update, context: CallbackContext):
    # b.write_user_position(update.message.chat_id, "main")

    user_id = update.message.from_user.id
    position = db_manager.get_user_position(user_id)[0]
    db_manager.debug_info()
    if position == "AddDeparture":
        response = short_report(update.message.text)
        if response != "Трек код не найден":

            db_manager.add_user_departures(user_id, update.message.text, response)
            keyboard = [
                [
                    InlineKeyboardButton("Полный отчет", callback_data='full_report|'+update.message.text),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(response, reply_markup=reply_markup)
        else:
            bot.send_message(update.message.chat_id, response)

    print(f"New message from {update.message.chat_id} , text : {update.message.text}")


def button(update: Update, context: CallbackContext):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
    if query.data.split("|")[0] == "full_report":
        query.edit_message_text(text=full_report(query.data.split("|")[1]))