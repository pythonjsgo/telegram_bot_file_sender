import random
import string
from functools import wraps

import telegram
from telegram import ChatAction

import config

bot = telegram.Bot(token=config.TOKEN)


def send_typing_action(func):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


"""
def update_stat(uuid):
    bot.editMessageText(message_id=)
    downloads = db.get_data_from_file(uuid, "downloads")
    uniq_downlaods = db.get_data_from_file(uuid, "uniq_downloads")
    downloads_with_subscribe = db.get_data_from_file(uuid, "downloads_with_subscribe")
    downloads_with_new_subscribe = db.get_data_from_file(uuid, "downloads_with_new_subscribe")
    update.message.reply_text(
        f"Ссылка - {deep_linked_url}\n📈 Статистика\n\nЗагрузки: {downloads}\nУникальные загрузки: {uniq_downlaods}\n\nЗагрузки с подпиской: {downloads_with_subscribe}\nЗагрузки с новой подпиской: {downloads_with_new_subscribe}",
        reply_markup=reply_markup)
    """


def add_admin(user_id):
    x = eval(open("admins.txt").read())
    x.append(user_id)
    config.admin_list.append(user_id)
    w = open("admins.txt", "w")
    w.write(str(x))
    w.close()


def delete_admin(user_id):
    x = eval(open("admins.txt").read())
    x.remove(user_id)
    config.admin_list.remove(user_id)
    w = open("admins.txt", "w")
    w.write(str(x))
    w.close()
