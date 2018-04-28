"""
Contains methods to parse JSON objects representing updates
"""
from botslib.MessageConstants import *
from botslib.errors.UnsupportedMessageType import UnsupportedMessageType


def get_message_json(update: dict) -> dict:
    """
    Gets json-like dict object with message info from the update

    :param update: json with update info
    :return: message dict
    """
    return update["message"]


def get_message_text(message_json: dict) -> str:
    """
    Extracts text from message json

    :param message_json: dict representing a message json
    :return: text sent by user in message if any, else None
    """
    return message_json["text"] if "text" in message_json else None


# TODO: exception on ["message"]?
def get_message_type(message_json: dict) -> int:
    """
    Returns type of message sent by user

    :param message_json: dict representing a message json
    :return: one of the constants listed in MessageConstants module
    :raises: UnsupportedMessageType
    """
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
    """
    Returns chat id of the given update

    :param update: json with update info
    :return: string with chat id
    """
    return str(update["message"]["chat"]["id"])


def get_update_id(update: dict) -> int:
    """
    Returns id of the given update

    :param update: json-like dict with update info
    :return: id of the update
    """
    return update["update_id"]


def get_user(update: dict) -> dict:
    """
    Extracts json-like dict object with user info from the update

    :param update: json with update info
    :return: json with user info
    """
    return update["message"]["from"]


# Groups don't have names, consider that
def get_user_name(user: dict) -> str:
    """
    Returns user's first and last name

    :param user: json with user info
    :return: first and last name of the user
    """
    try:
        last_name = user["last_name"]
    except KeyError:
        last_name = ""
    return user["first_name"] + (" " + last_name if last_name else "")


# str because of shelve
def get_user_id(user: dict) -> str:
    """
    Returns user's id

    :param user: json with user info
    :return: id of user
    """
    return str(user["id"])
