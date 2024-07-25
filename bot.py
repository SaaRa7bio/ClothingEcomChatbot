from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton
)
from telegram.ext import (
    CallbackQueryHandler,
    CallbackContext,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters,
    ApplicationBuilder
)
import logging
from logic import Bot



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

#this class will handle logic and run the bot
class MainBot:
    @staticmethod
    def main():

        application = ApplicationBuilder().token('replace-with-real-token').build()


        bot = Bot()


        handlers = [
            CommandHandler("start", bot.start),
            CallbackQueryHandler(bot.purchase, pattern="purchase"),
            CallbackQueryHandler(bot.customer_service, pattern='customerService'),
            CallbackQueryHandler(bot.cat_opts, pattern='^opt'),
            CallbackQueryHandler(bot.purchase, pattern='back_to_main'),
            CallbackQueryHandler(bot.display_size, pattern='^size'),
            CallbackQueryHandler(bot.cat_opts, pattern='back_to_options'),
            CallbackQueryHandler(bot.table, pattern='table'),
            CallbackQueryHandler(bot.colors, pattern='^colors'),
            CallbackQueryHandler(bot.check, pattern='^check'),
            CallbackQueryHandler(bot.display_size, pattern='back_to_size'),
            CallbackQueryHandler(bot.colors, pattern='back_to_colors'),
            CallbackQueryHandler(bot.auth, pattern="auth"),
            CallbackQueryHandler(bot.add2Cart, pattern="displayCart"),
            CallbackQueryHandler(bot.addanother, pattern="addanother"),
            CallbackQueryHandler(bot.cancel_cart, pattern="cancel_cart"),
            CallbackQueryHandler(bot.check, pattern="back2check"),
            CallbackQueryHandler(bot.location, pattern="location"),
            CallbackQueryHandler(bot.process_location, pattern='^city_'),
            CallbackQueryHandler(bot.summarize_location, pattern='^sub_'),
            MessageHandler(filters.Regex(r'^street.*$'), bot.request_phone),
            MessageHandler(filters.Regex(r'^\d+$'), bot.phone_verified),
            CallbackQueryHandler(bot.increment, pattern="increment")

        ]


        application.add_handlers(handlers)

        application.run_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Application started polling")

if __name__ == '__main__':
    logger.info("Main function called")
    MainBot.main()