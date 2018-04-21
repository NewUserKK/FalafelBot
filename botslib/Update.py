from botslib.UpdateJsonParser import *


class Update:
    def __init__(self, update_json: dict):
        self.chat_id = get_chat_id(update_json)

        self.user = get_user(update_json)
        self.user_id = get_user_id(self.user)
        self.user_name = get_user_name(self.user)

        self.message_json = get_message_json(update_json)
        self.message_type = get_message_type(self.message_json)
