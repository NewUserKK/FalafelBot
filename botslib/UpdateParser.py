from botslib.MessageConstants import *
from botslib.errors.UnsupportedMessageType import UnsupportedMessageType


def get_message_json(update: dict) -> dict:
    return update["message"]


def get_message_text(message_json: dict) -> str:
    return message_json["text"]


# TODO: exception on ["message"]?
def get_message_type(message_json: dict) -> int:
    if "text" in message_json:
        return TEXT
    if "audio" in message_json:
        return AUDIO
    if "document" in message_json:
        return DOCUMENT
    if "photo" in message_json:
        return PHOTO
    if "sticker" in message_json:
        return STICKER
    if "video" in message_json:
        return VIDEO
    if "voice" in message_json:
        return VOICE
    if "video_note" in message_json:
        return VIDEO_NOTE
    if "game" in message_json:
        return GAME
    if "contact" in message_json:
        return CONTACT
    if "location" in message_json:
        return LOCATION
    if "caption" in message_json:
        return CAPTION
    if "venue" in message_json:
        return VENUE
    raise UnsupportedMessageType


def get_chat_id(update: dict) -> str:
    return str(update["message"]["chat"]["id"])


def get_update_id(update: dict) -> int:
    return update["update_id"]


def get_user(update: dict) -> dict:
    return update["message"]["from"]


# Groups don't have names, consider that
def get_user_name(user: dict) -> str:
    try:
        last_name = user["last_name"]
    except KeyError:
        last_name = ""
    return user["first_name"] + " " + last_name


# str because of shelve
def get_user_id(user: dict) -> str:
    return str(user["id"])