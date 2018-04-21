import sys
import shelve

from random import randint
from datetime import datetime
from botslib.Update import *
from botslib.UpdateJsonParser import *
from botslib.errors.UnsupportedMessageType import *
from botslib.BotHandler import *
from botslib.MessageConstants import *


class FalafelBot(BotHandler):

    def __init__(self, token, log_name=None):
        """
        Performs initialization of bot

        Creates current session users database,
        opens or creates overall users database and motivation notes database
        using shelve module. Names should be "users_db.shb" and "motivation.shb".

        :param token: bot token
        :param log_name: name of log file if necessary
        """
        # TODO: add various db names support
        super().__init__(token)
        self.log_name = log_name
        self.log_file = None
        self.session_users_db = {}
        self.overall_users_db = shelve.open("users_db.shb")
        self.motivation_notes_db = shelve.open("motivation.shb")

        self.out_message = ""

    def run(self) -> None:
        """
        Entry point for bot running

        Opens logs and starts main loop
        """
        self.open_log()
        self.log_write("Bot started!", restart=True)
        self.log_write("Overall db: " + str(dict(self.overall_users_db)))
        self.mainloop()    
    
    def mainloop(self) -> None:
        """
        Starts a main endless loop for the bot.

        At each iteration gets list of updates from Telegram API and respond for every request
        Currently supports text messages and some stickers (untested yet due to the best laws of our country)
        """
        while True:
            try:
                updates = self.get_updates_list()
            except BadResponseError:
                continue

            for update in updates:
                try:
                    update = self.get_update_object(update)
                except UnsupportedMessageType:
                    self.log_write("Unsupported message type! JSON:\n" + str(update.message_json))
                    self.send_message(update.chat_id, "What is it?")
                    self._inc_offset()
                    continue

                if update.message_type == TEXT:
                    self.on_text(update)

                elif update.message_type == STICKER:
                    self.log_write(update.user_name + " sent sticker")
                    self.on_sticker(update)

                else:
                    self.send_message(update.chat_id, "Use /help")

                self._inc_offset()

    def on_text(self, update: Update) -> None:
        """
        Responds to text message sent by user

        :param update: current update object
        """

        def get_default_message() -> str:
            default_messages = ["Не внятно!",
                                "Не содержательно!",
                                "Эту реплику из зала я отвергну как неорганизованную!"]
            return (default_messages[randint(0, len(default_messages) - 1)] +
                    " Используйте /help")

        msg_parse_mode = None
        query = get_message_text(update.message_json)

        if query == "/help" or query == "/start":
            self.out_message = self.get_help_message()

        elif query == "/reg":
            self._on_registration(update)

        elif query == "/leave":
            self._on_leave(update)

        elif query == "/list":
            if self._on_list_query():
                msg_parse_mode = "Markdown"

        elif query == "/roll":
            self._on_roll(update)

        elif query == "/motivate":
            # TODO: self._on_motivate()
            self.out_message = get_default_message()

        elif query.startswith("/logs"):
            lines = self.parse_args(query)
            self.out_message = self.get_log(lines)

        else:
            self.out_message = get_default_message()

        self.send_message(update.chat_id, self.out_message, msg_parse_mode)

    def _on_registration(self, update: Update) -> None:
        if update.user_id not in self.session_users_db:
            self.register_user(update.user)
            self.out_message = "Registered!"
        else:
            self.out_message = "Already registered!"

    def register_user(self, user: dict) -> None:
        """
        Registers user as participant of roll and adds him to databases
        If user already registered, does nothing

        :param user: json-like dict object representing user
        """
        user_id = get_user_id(user)
        if user_id in self.session_users_db:
            return

        if user_id not in self.overall_users_db:
            self.overall_users_db[user_id] = get_user_name(user)

        self.session_users_db[user_id] = self.overall_users_db[user_id]

    def _on_leave(self, update: Update) -> None:
        if update.user_id in self.session_users_db:
            self.session_users_db.pop(update.user_id)
            self.out_message = "Goodbye!"
        else:
            self.out_message = "You can't leave if you didn't register!"

    def _on_list_query(self) -> bool:
        # returns false if user list is empty
        if not self.session_users_db:
            self.out_message = "No one is eating shaverma today :("
            return False
        else:
            self.out_message = ("*List of users:*\n\n" +
                                "\n".join(self.session_users_db.values()))
            return True

    def _on_roll(self, update: Update) -> None:
        self.out_message = "{} has started a roll!\n\n".format(update.user_name)

        if update.user_id not in self.session_users_db:
            self.send_message(update.user_id, "Autoregistered!")
            self.register_user(update.user)

        self.log_write("Rolling for: " + str(self.session_users_db))

        lucky_index = randint(0, len(self.session_users_db) - 1)
        lucky_guy = list(self.session_users_db.keys())[lucky_index]
        self.out_message += "Sorry, you lose, {}".format(self.session_users_db[lucky_guy])

    # Not working yet, bd is broken
    def _on_motivate(self) -> None:
        note_num = str(randint(1, len(self.motivation_notes_db)))
        self.out_message = note_num + ". " + self.motivation_notes_db[note_num]

    def on_sticker(self, update: Update) -> None:
        """
        Responds to sticker sent by user

        :param update: current update object
        """
        sticker = update.message_json["sticker"]
        sticker_id = sticker["file_id"]
        # Ryzhkov: left -> right
        if sticker_id == "CAADAgADdAEAAizdvQn2LxfsJBfaxAI":
            self.send_sticker(update.chat_id, "CAADAgADcgEAAizdvQlKOeQLRsy97AI")

        # Ryzhkov: right -> left
        elif sticker_id == "CAADAgADcgEAAizdvQlKOeQLRsy97AI":
            self.send_sticker(update.chat_id, "CAADAgADdAEAAizdvQn2LxfsJBfaxAI")

        # Shalyto: left -> right
        elif sticker_id == "CAADAgADUQADRTARC-8FwsYxJM2cAg":
            self.send_sticker(update.chat_id, "CAADAgADTgADRTARC8Mi8Smz4tpGAg")

        # Shalyto: right -> left
        elif sticker_id == "CAADAgADTgADRTARC8Mi8Smz4tpGAg":
            self.send_sticker(update.chat_id, "CAADAgADUQADRTARC-8FwsYxJM2cAg")

        # Shalyto: both
        elif sticker_id == "CAADAgADUgADRTARC-jA-35mcixwAg":
            self.send_sticker(update.chat_id, "CAADAgADUgADRTARC-jA-35mcixwAg")

        # Default
        else:
            self.send_sticker(update.chat_id, "CAADAgADSAIAAkcGQwU-G-9SZUDTWAI")

    def open_log(self, mode='a') -> None:
        """
        Opens log file if there is any with append mode by default

        :param mode: mode of opening, same as standard open() modes
        """
        if self.log_name:
            self.log_file = open(self.log_name, mode)

    def log_write(self, message: str, restart=False, console=True) -> None:
        """
        Writes message to log file and/or console
        Format: [hh:mm:ss] <message>

        :param message: message to write
        :param restart: if True, prints line that indicates restart of the bot
        :param console: if True, prints message to the console
        """
        log_message = "{2}[{0}] {1}\n".format(
                datetime.now().isoformat(" ")[:-7],  # [:-7] cuts nanoseconds from output
                message,
                "\n====== RESTART ======\n" if restart else "")

        if console:
            print(log_message)

        if self.log_name:
            self.log_file.write(log_message)

    def get_log(self, last_messages_amount=10) -> str:
        """
        Returns last messages of the log

        :param last_messages_amount: amount of messages to return
        :return: string contains last_messages_amount log messages
        """

        if not self.log_name:
            return "Actions weren't logging"

        self.open_log('r')
        log_dump = self.log_file.readlines()

        if last_messages_amount > len(log_dump):
            last_messages = "".join(log_dump)
        else:
            last_messages = "".join(log_dump[-last_messages_amount:])

        self.open_log('a')
        return last_messages

    def close_db(self) -> None:
        """ Closes all opened logs and databases """
        self.log_write("Logs and DB closed")
        if self.log_name:
            self.log_file.close()
        self.motivation_notes_db.close()
        self.overall_users_db.close()

    @staticmethod
    def get_update_object(update_json: dict) -> Update:
        """
        Converts json to Update object

        :param update_json: json-like dict object
        :return: Update object created from json
        """
        return Update(update_json)

    @staticmethod
    def get_help_message() -> str:
        """
        Returns message displayed on /help command

        :return: help message
        """
        return ("Usage:\n"
                "/help - print this message\n"
                "/reg - register for roll\n"
                "/leave - unregister"
                "/list - show list of participants\n"
                "/roll - find the lucky guy")

    @staticmethod
    def parse_args(message: str) -> int:
        """
        Parses arguments splitted by spaces
        Currently parses only one and int argument so use with caution

        :param message: message to parse
        :return: argument
        """
        # TODO: return list of arguments
        command = message.split(" ")
        arg = None
        try:
            arg = int(command[1])
        except ValueError:
            pass
        except IndexError:
            pass
        return arg


if __name__ == "__main__":
    try:
        bot = FalafelBot(sys.argv[1], "queuebot.log")
    except IndexError:
        raise AttributeError("Incorrect token!")

    bot.run()
