import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler

import config
from handlers import StartHandler, button, GetFileHandler, CreateFileLinkHandler, ChannelsAndChatsHandler, \
    AdminsHandler, CHOOSING, TYPING_CHOICE, TYPING_REPLY, StatisticsHandler, other
from tools import add_admin

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    updater = Updater(config.TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', StartHandler))
    dispatcher.add_handler(MessageHandler(Filters.document, CreateFileLinkHandler))
    dispatcher.add_handler(MessageHandler(Filters.regex("Каналы"), ChannelsAndChatsHandler))
    dispatcher.add_handler(MessageHandler(Filters.regex("Администраторы"), AdminsHandler))
    dispatcher.add_handler(MessageHandler(Filters.regex("Статистика"), StatisticsHandler))
    dispatcher.add_handler(MessageHandler(Filters.text, other))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()


if __name__ == '__main__':
    main()
