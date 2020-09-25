from telegram.error import Unauthorized
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode, TelegramError
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
        self.updater = Updater(telegram_token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Add Commands to bot
        self._addCommand(CommandHandler("start", self.start))
        self._addCommand(CommandHandler("stop", self.stop))
        self._addCommand(CommandHandler("help", self.help))
        self._addCommand(CommandHandler("list", self.list))
        self._addCommand(CommandHandler("about", self.about))
        self._addCommand(CommandHandler("add", self.add, pass_args=True))
        self._addCommand(CommandHandler("get", self.get, pass_args=True))
        self._addCommand(CommandHandler("remove", self.remove, pass_args=True))

        # Start the bot
        self.processing = BatchProcess(
            database=self.db, update_interval=update_interval, bot=self.dispatcher.bot
        )

        self.processing.start()
        self.updater.start_polling()
        self.updater.idle()

    def _addCommand(self, command):
        """Registers a new command to the bot"""
        self.updater.dispatcher.add_handler(command)

    def start(self, update, context):
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

    def add(self, update, context):
        """
        Adds a rss subscription to user
        """

        telegram_user = update.message.from_user

        if len(context.args) != 2:
            message = "Sorry! I could not add the entry! Please use the the command passing the following arguments:\n\n /add <url> <entryname> \n\n Here is a short example: \n\n /add http://www.feedforall.com/sample.xml ExampleEntry"
            update.message.reply_text(message)
            return
        print(f'context.args: {context.args}')
        # arg_url = FeedHandler.format_url_string(string=context.args[0])
        arg_url = context.args[0]
        arg_entry = context.args[1]
        print(f'arg_entry: {arg_entry}')
        print(f'arg_url: {arg_url}')

        # Check if argument matches url format
        # if not FeedHandler.is_parsable(url=arg_url):
        #     message = (
        #         "Sorry! It seems like '"
        #         + str(arg_url)
        #         + "' doesn't provide an RSS news feed.. Have you tried another URL from that provider?"
        #     )
        #     update.message.reply_text(message)
        #     return

        # Check if entry does not exists
        entries = self.db.get_urls_for_user(telegram_id=telegram_user.id)
        print(entries)

        if any(arg_url in entry for entry in entries):
            message = (
                "Sorry, "
                + telegram_user.first_name
                + "! I already have that url with stored in your subscriptions."
            )
            update.message.reply_text(message)
            return

        if any(arg_entry in entry for entry in entries):
            message = (
                "Sorry! I already have an entry with name "
                + arg_entry
                + " stored in your subscriptions.. Please choose another entry name or delete the entry using '/remove "
                + arg_entry
                + "'"
            )
            update.message.reply_text(message)
            return

        self.db.add_user_bookmark(
            telegram_id=telegram_user.id, url=arg_url, alias=arg_entry
        )
        message = "I successfully added " + arg_entry + " to your subscriptions!"
        update.message.reply_text(message)

    def get(self, update, context):
        """
        Manually parses an rss feed
        """

        telegram_user = update.message.from_user

        if len(context.args) == 0:
            message = "no argument please put atleast one To get the last news of your subscription please use /get <entryname> [optional: <count 1-10>]. Make sure you first add a feed using the /add command."
            update.message.reply_text(message)
            return

        if len(context.args) > 2:
            message = "To get the last news of your subscription please use /get <entryname> [optional: <count 1-10>]. Make sure you first add a feed using the /add command."
            update.message.reply_text(message)
            return

        if len(context.args) == 2:
            args_entry = context.args[0]
            args_count = int(context.args[1])
        else:
            args_entry = context.args[0]
            args_count = 4

        url = self.db.get_user_bookmark(telegram_id=telegram_user.id, alias=args_entry)
        print(context.args)
        if url is None:
            message = (
                "I can not find an entry with label "
                + args_entry
                + "in your subscriptions! Please check your subscriptions using /list and use the delete command "
                "again! "
            )
            update.message.reply_text(message)
            return

        entries = FeedHandler.parse_feed(url[0], args_count)
        for entry in entries:
            message = (
                "[" + url[1] + "] <a href='" + entry.link + "'>" + entry.title + "</a>"
            )
            print(message)

            try:
                update.message.reply_text(message, parse_mode=ParseMode.HTML)
            except Unauthorized:
                self.db.update_user(telegram_id=telegram_user.id, is_active=0)
            except TelegramError:
                # handle all other telegram related errors
                pass

    def remove(self, update, context):
        """
        Removes an rss subscription from user
        """

        telegram_user = update.message.from_user
        if len(context.args) != 1:
            message = (
                "To remove a subscriptions from your list please use /remove <entryname>. To see all your "
                "subscriptions along with their entry names use /list ! "
            )
            update.message.reply_text(message)
            return

        entry = self.db.get_user_bookmark(telegram_id=telegram_user.id, alias=context.args[0])
        if entry:
            self.db.remove_user_bookmark(telegram_id=telegram_user.id, url=entry[0])
            message = "I removed " + context.args[0] + " from your subscriptions!"
            update.message.reply_text(message)
        else:
            message = (
                "I can not find an entry with label "
                + context.args[0]
                + "in your subscriptions! Please check your subscriptions using /list and use the delete command "
                "again! "
            )
            update.message.reply_text(message)

    def stop(self, update, context):
        """Stops the bot from working"""

        telegram_user = update.message.from_user
        self.db.update_user(telegram_id=telegram_user.id, is_active=0)

        message = "Deactivated use the /start comand to restart bot"
        update.message.reply_text(message)

    def list(self, update, context):
        """Displays user feeds"""
        telegram_user = update.message.from_user

        message = "Here is the list of all your subs"
        update.message.reply_text(message)

        entries = self.db.get_urls_for_user(telegram_id=telegram_user.id)

        for entry in entries:
            message = "[" + entry[1] + "]\n " + entry[0]
            update.message.reply_text(message)

    def help(self, update, context):
        """Send a message when the command /help is used"""

        message = "Do you need help \n Help menu shows here🤞"
        update.message.reply_text(message)

    def about(self, update, context):
        """Show about information"""

        message = (
            "Thank you for using my Bot \n"
            "<a href='https://chuckzokoye.com/'>ChuckzBot</a> \n"
        )
        update.message.reply_text(message, parse_mode=ParseMode.HTML)


if __name__ == "__main__":
    # Load Credentials
    fh = FileHandler("..")
    credentials = fh.load_json("resources/credentials.json")

    # Pass Credentials to bot
    token = credentials["telegram_token"]
    update = credentials["update_interval"]
    UpworkRss(telegram_token=token, update_interval=update)
