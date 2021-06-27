import telegram
from telegram import Update, ReplyKeyboardMarkup, ChatAction, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.utils import helpers

import config
import keyboards
import tools
from db_manager import DB_manager
from tools import send_typing_action

bot = telegram.Bot(token=config.TOKEN)

db = DB_manager()
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


@send_typing_action
def GetFileHandler(update: Update, context: CallbackContext):
    # b.write_user_position(update.message.chat_id, "main")

    print(f"New message from {update.message.chat_id} , text : {update.message.text}")

    user_id = update.message.from_user.id


@send_typing_action
def StartHandler(update: Update, context: CallbackContext):
    # b.write_user_position(update.message.chat_id, "main")

    print(f"New message from {update.message.chat_id} , text : {update.message.text}")
    user_id = update.message.from_user.id
    db.update_user_position(user_id, "StartHandler")

    if update.message.text != "/start":
        uuid = update.message.text[7:]
        if db.get_file_id(uuid):
            print(db.get_channel_url(uuid).replace(" ", ""))
            keyboard = [
                [
                    InlineKeyboardButton("Подписаться на канал", url="t.me/" + db.get_channel_url(uuid)[2:]),
                    InlineKeyboardButton("Проверить подписку", callback_data="send_doc|" + uuid),
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            channel_id = db.get_file_channel(uuid)
            print(channel_id)
            status = bot.getChatMember(chat_id=channel_id, user_id=user_id).status
            if db.get_file_id(uuid):
                if status == "creator" or status == "administrator" or status == "member":
                    print(db.get_file_id(uuid)[0])
                    description = db.get_data_from_file(uuid, "description")
                    if description != "None":
                        update.message.reply_document(db.get_file_id(uuid)[0], caption=description)
                    else:
                        update.message.reply_document(db.get_file_id(uuid)[0])

                    db.increase("downloads", uuid)
                    db.increase("downloads_with_subscribe", uuid)
                    if db.get_if_download(user_id=user_id, uuid=uuid):
                        print("Cкачано раньше")

                    else:
                        print("В первыйц раз")
                        db.increase("uniq_downloads", uuid)
                        db.add_download(user_id, uuid)
                    update_message(user_id, uuid)
                else:
                    update.message.reply_text(f"Для получения файла подпишитесь на канал", reply_markup=reply_markup)
            else:
                update.message.reply_text("Файл не найден")
        else:
            update.message.reply_text("Файл не найден")
    else:
        if user_id in config.admin_list:
            reply_markup = ReplyKeyboardMarkup(keyboards.keyboard_admin_start)
            update.message.reply_text("Приветствую, Администратор! ", reply_markup=reply_markup)

        # update.message.reply_text('Отправьте файл, чтобы получить ссылку')


def CreateFileLinkHandler(update: Update, context: CallbackContext):
    print(f"New message from {update.message.chat_id} , text : {update.message.caption}")
    user_id = update.message.from_user.id
    if user_id in config.admin_list:
        if not db.get_selected_channel_id(user_id) == "":
            update.message.reply_document(update.message.document.file_id)
            uuid = tools.get_random_string(10)
            channel_id = db.get_selected_channel_id(user_id)
            print(channel_id, "djklshjkhdjksdf")
            db.add_file_id(update.message.document.file_id, uuid, description=update.message.caption,
                           channel_id=channel_id,
                           channel_url=db.get_channel_url_by_id(channel_id))
            # print(db.get_file_channel(update.message.document.file_id))
            keyboard = []

            deep_linked_url = helpers.create_deep_linked_url(bot.username, uuid)
            keyboard = [
                [
                    InlineKeyboardButton("Добавить описание", callback_data="add_description|" + uuid),
                ], [
                    InlineKeyboardButton("Удалить файл", callback_data="delete_file|" + uuid),
                ],
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)
            downloads = db.get_data_from_file(uuid, "downloads")
            uniq_downlaods = db.get_data_from_file(uuid, "uniq_downloads")
            downloads_with_subscribe = db.get_data_from_file(uuid, "downloads_with_subscribe")
            downloads_with_new_subscribe = db.get_data_from_file(uuid, "downloads_with_new_subscribe")
            description = db.get_data_from_file(uuid, "description")
            msg = update.message.reply_text(
                f"Ссылка - {deep_linked_url}\nОписание: {description}\n📈 Статистика\n\nЗагрузки: {downloads}\nУникальные загрузки: {uniq_downlaods}\n\nЗагрузки с подпиской: {downloads_with_subscribe}\nЗагрузки с новой подпиской: {downloads_with_new_subscribe}",
                reply_markup=reply_markup)
            db.update_message_id(message_id=msg.message_id, uuid=uuid, deep_linked_url=deep_linked_url)
        else:
            update.message.reply_text("Пожалуйста выберете канал в разделе 'Каналы'")


def ChannelsAndChatsHandler(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    db.update_user_position(user_id, "ChannelsAndChatsHandler")
    keyboard = [
        [
            InlineKeyboardButton("Добавить канал", callback_data="add_channel"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    channels = db.get_channels()
    if len(channels) == 0:
        update.message.reply_text("Не найдено", reply_markup=reply_markup)
    else:
        keyboard = []
        for channel in channels:
            print(type(channel), "Rfftyft")
            keyboard.append([InlineKeyboardButton(channel[0], callback_data="select_channel|" + channel[1])])
            keyboard.append([InlineKeyboardButton("Удалить ❌", callback_data="delete_channel|" + channel[1])])

            reply_markup = InlineKeyboardMarkup(keyboard)
        keyboard.append([InlineKeyboardButton("Добавить канал", callback_data="add_channel")])
        update.message.reply_text("Выберете канал", reply_markup=reply_markup)


def AdminsHandler(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    db.update_user_position(user_id, "AdminsHandler")
    keyboard = [[]]
    for admin in config.admin_list:
        keyboard.append([InlineKeyboardButton(str(admin) + " ❌", callback_data="delete_admin|" + str(admin))])

    keyboard.append([InlineKeyboardButton("Добавить администратора", callback_data="add_admin")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Администраторы:", reply_markup=reply_markup)


def StatisticsHandler(update: Update, context: CallbackContext):
    db.sql.execute("SELECT * FROM files")
    files = db.sql.fetchall()
    print(files)

    if len(files) == 0: update.message.reply_text("Не найдено")
    for file in files:
        uuid = file[1]
        downloads, uniq_downlaods, downloads_with_subscribe, downloads_with_new_subscribe, description = db.get_file_stat(
            uuid)
        update.message.reply_text(
            f"Ссылка {db.get_message_deep_link(uuid=uuid)} \nЗагрузки: {downloads}\n Уникальные загрузки: {uniq_downlaods}\n Загрузки с подпиской: {downloads_with_subscribe}\n Загрузки с новой подпиской: {downloads_with_new_subscribe}"

        )


def update_message(user_id, uuid):
    deep_linked_url = db.get_message_deep_link(uuid)
    downloads, uniq_downlaods, downloads_with_subscribe, downloads_with_new_subscribe, description = db.get_file_stat(
        uuid)
    message_id = db.get_message_id(uuid=uuid)
    bot.editMessageText(message_id=message_id, chat_id=user_id,
                        text=f"Ссылка - {deep_linked_url}\nОписание: {description}\n📈 Статистика\n\nЗагрузки: {downloads}\nУникальные загрузки: {uniq_downlaods}\n\nЗагрузки с подпиской: {downloads_with_subscribe}\nЗагрузки с новой подпиской: {downloads_with_new_subscribe}")


def button(update: Update, context: CallbackContext):
    query = update.callback_query
    print(query.data)
    user_id = query.from_user.id
    type = query.data.split("|")[0]

    if type == "add_channel":
        bot.send_message(user_id, "ID канала:")
        db.update_user_position(user_id, "ChannelsAndChatsHandler_input_channel_id")

    if type == "add_admin":
        bot.send_message(user_id, "UserID администратора:")
        db.update_user_position(user_id, "ChannelsAndChatsHandler_input_admin_id")

    if type == "send_doc":
        uuid = query.data.split("|")[1]
        status = bot.getChatMember(chat_id=db.get_file_channel(uuid), user_id=user_id).status
        if status == "creator" or status == "administrator" or status == "member":
            bot.send_document(chat_id=user_id, document=db.get_file_id(uuid)[0])
            db.increase("downloads", uuid)
            db.increase("downloads_with_subscribe", uuid)
            if db.get_if_download(user_id=user_id, uuid=uuid):
                print("Cкачано раньше")

            else:
                print("В первыйц раз")
                db.increase("downloads_with_new_subscribe", uuid)
                db.increase("uniq_downloads", uuid)
                db.add_download(user_id, uuid)
            update_message(user_id, uuid)

        else:
            bot.send_message(chat_id=user_id, text="Подписка не найдена!")
    if type == "add_description":
        pass
    if type == "select_channel":
        db.update_user_position(user_id, selected_channel_id=query.data.split("|")[1])
        bot.send_message(user_id, f"Выбран канал " + db.get_channel_url_by_id(query.data.split("|")[1]))

    if type == "delete_channel":
        db.delete_channel(query.data.split("|")[1])
        bot.send_message(user_id, "Канал удален")
        db.update_user_position(user_id, "ChannelsAndChatsHandler")
        keyboard = [
            [
                InlineKeyboardButton("Добавить канал", callback_data="add_channel"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
        channels = db.get_channels()
        if len(channels) == 0:
            bot.send_message(user_id, "Не найдено", reply_markup=reply_markup)
        else:
            keyboard = []
            for channel in channels:
                keyboard.append([InlineKeyboardButton(channel[0], callback_data="select_channel|" + channel[1])])
                keyboard.append([InlineKeyboardButton("Удалить ❌", callback_data="delete_channel|" + channel[1])])

                reply_markup = InlineKeyboardMarkup(keyboard)
            keyboard.append([InlineKeyboardButton("Добавить канал", callback_data="add_channel")])
            bot.send_message(user_id, "Выберете канал", reply_markup=reply_markup)

    if type == "delete_admin":
        tools.delete_admin(int(query.data.split("|")[1]))
        bot.send_message(user_id, "Админ удален")
        db.update_user_position(user_id, "AdminsHandler")
        keyboard = [[]]
        for admin in config.admin_list:
            keyboard.append([InlineKeyboardButton(str(admin) + " ❌", callback_data="delete_admin|" + str(admin))])

        keyboard.append([InlineKeyboardButton("Добавить администратора", callback_data="add_admin")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        bot.send_message(user_id, "Администраторы:", reply_markup=reply_markup)
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()


def other(update: Update, context: CallbackContext):
    print(update.message.text)
    user_id = update.message.from_user.id
    print(db.get_user_position(user_id))
    position = db.get_user_position(user_id)
    if position == "ChannelsAndChatsHandler_input_channel_id":
        if update.message.text[1:].isdigit():
            db.update_user_position(user_id, position="ChannelsAndChatsHandler_input_channel_url",
                                    current_channel_id=update.message.text)
            bot.send_message(user_id, "Никнейм канала, с @")
        else:
            update.message.reply_text("Неверный id")

    if position == "ChannelsAndChatsHandler_input_admin_id":
        if update.message.text.isdigit():
            tools.add_admin(int(update.message.text))
            update.message.reply_text("Админ успешно добавлен!")
            db.update_user_position(user_id, "AdminsHandler")
            keyboard = [[]]
            for admin in config.admin_list:
                keyboard.append([InlineKeyboardButton(str(admin) + " ❌", callback_data="delete_admin|" + str(admin))])

            keyboard.append([InlineKeyboardButton("Добавить администратора", callback_data="add_admin")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            bot.send_message(user_id, "Администраторы:", reply_markup=reply_markup)

        else:
            update.message.reply_text("Неверный id")

    if position == "ChannelsAndChatsHandler_input_channel_url":
        if update.message.text[0] == "@":
            db.add_channel(db.get_current_channel_id(user_id), update.message.text)
            bot.send_message(user_id, "Канал добавлен")
        else:
            update.message.reply_text("Неверное имя канала")
