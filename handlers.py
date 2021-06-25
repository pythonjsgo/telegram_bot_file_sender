import telegram
from telegram import Update, ReplyKeyboardMarkup, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.utils import helpers
import uuid

import config
import tools
from db_manager import DB_manager
from tools import send_typing_action

bot = telegram.Bot(token=config.TOKEN)
db = DB_manager()
bot = telegram.Bot(token=config.TOKEN)


@send_typing_action
def GetFileHandler(update: Update, context: CallbackContext):
    # b.write_user_position(update.message.chat_id, "main")

    print(f"New message from {update.message.chat_id} , text : {update.message.text}")

    user_id = update.message.from_user.id


def CreateFileLinkHandler(update: Update, context: CallbackContext):
    print(f"New message from {update.message.chat_id} , text : {update.message.text}")
    user_id = update.message.from_user.id
    if user_id in config.admin_list:
        update.message.reply_document(update.message.document.file_id)
        uuid = tools.get_random_string(10)
        db.add_file_id(update.message.document.file_id, uuid)
        deep_linked_url = helpers.create_deep_linked_url(bot.username, uuid)
        update.message.reply_text("Link " + deep_linked_url)


@send_typing_action
def StartHandler(update: Update, context: CallbackContext):
    # b.write_user_position(update.message.chat_id, "main")

    print(f"New message from {update.message.chat_id} , text : {update.message.text}")
    user_id = update.message.from_user.id
    db.update_user_position(user_id, "StartHandler")
    if update.message.text != "/start":
        print(update.message.text[7:])
        keyboard = [
            [
                InlineKeyboardButton("Проверить подписку", callback_data=update.message.text[7:]),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        status = bot.getChatMember(chat_id=config.channel_id, user_id=user_id).status
        if status == "creator" or status == "administrator" or status == "member":
            print(db.get_file_id(update.message.text[7:])[0])
            update.message.reply_document(db.get_file_id(update.message.text[7:])[0])
        else:
            update.message.reply_text(f"Для получения файла подпишитесь на канал {config.channel_name}",
                                      reply_markup=reply_markup)


    else:
        if user_id in config.admin_list:
            update.message.reply_text("Приветствую, Администратор! ")
            update.message.reply_text('Отправьте файл, чтобы получить ссылку')


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    print(query.data)
    user_id = query.from_user.id
    status = bot.getChatMember(chat_id=-1001589540427, user_id=user_id).status
    if status == "creator" or status == "administrator" or status == "member":
        print(db.get_file_id(query.data)[0])
        bot.send_document(chat_id=user_id, document=db.get_file_id(query.data)[0])
    else:
        bot.send_message(chat_id=user_id, text="Подписка не найдена!")

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()
