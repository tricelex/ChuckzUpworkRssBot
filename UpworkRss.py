from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
from util.filehandler import FileHandler
from util.database import DatabaseHandler
from util.processing import BatchProcess
from util.feedhandler import FeedHandler


class UpworkRss(object):
    def __init__(self, telegram_token, update_interval):
        # Initialize bot internals
        self.db = DatabaseHandler("resources/datastore.db")
        self.fh = FileHandler("..")

        # Register webhook to telegram bot
        self.updater = Updater(telegram_token)
        self.dispatcher = self.updater.dispatcher

        # Add Commands to bot
        self._addCommand(CommandHandler("start", self.start))

        print("Hello World")

    def _addCommand(self, command):
        """Registers a new command to the bot"""
        self.updater.dispatcher.add_handler(command)

    def start(self, bot, update):
        """Send a message when the command /start is issued"""

        telegram_user = update.message.from_user

        # Add new User if not exist
        if not self.db.get_user(telegram_id=telegram_user.id):
            message = (
                "Hello! I don't think we've met before! I am an RSS News Bot and would like to help you to "
                "receive your favourite news in the future! Let me first set up a few things before we start... "
            )
            update.message.reply_text(message)
            self.db.add_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                firstname=telegram_user.first_name,
                lastname=telegram_user.last_name,
                language_code=telegram_user.language_code,
                is_bot=telegram_user.is_bot,
                is_active=1,
            )
        self.db.update_user(telegram_id=telegram_user.id, is_active=1)
        message = "You will now receive news! Use /help if you need some tips!"
        update.message.reply_text(message)


if __name__ == "__main__":
    # Load Credentials
    fh = FileHandler("..")
    credentials = fh.load_json("resources/credentials.json")

    # Pass Credentials to bot
    token = credentials["telegram_token"]
    update = credentials["update_interval"]
    UpworkRss(telegram_token=token, update_interval=update)
