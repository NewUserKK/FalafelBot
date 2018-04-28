import requests

from botslib.errors.BadResponseError import BadResponseError


class BotHandler(object):
    """
    Class for interacting with Telegram API
    """
    def __init__(self, token: str):
        """
        Initialize a bot with token joined with Telegram API-link

        :param token: token needed to access the bot
        """
        self._api_url = "https://api.telegram.org/{}/".format(token)
        self._last_offset = None
        self.last_response = None

    def _inc_offset(self) -> None:
        if self._last_offset is None:
            self._last_offset = self.last_response["result"][0]["update_id"]
        self._last_offset += 1

    def get_updates_json(self, offset=None, timeout=30) -> dict:
        """
        Makes a request to bot API and gets json with results of request

        :param offset: offset used for long-polling
        :param timeout: long-polling timeout in seconds
        :return: json-like dict object with response
        """
        if offset is None:
            offset = self._last_offset

        method = "getUpdates"
        params = {"offset": offset, "timeout": timeout}
        response = requests.get(self._api_url + method, params)
        self.last_response = response.json()
        return self.last_response

    def get_updates_list(self) -> list:
        """
        Gets list of updates from update json

        :return: list of updates
        :raises: BadResponseError if API returned bad response
        """
        if not self.get_updates_json()["ok"]:
            raise BadResponseError
        return self.get_updates_json(self._last_offset)["result"]

    def send_message(self, chat_id: str, message: str, parse_mode=None) -> requests.Response:
        """
        Sends message in chat

        :param chat_id: id of destination chat
        :param message: message to send
        :param parse_mode: message parse mode, could be "Markdown" or None
        :return: API response to request
        """
        method = "sendMessage"
        params = {"chat_id": chat_id, "text": message}
        if parse_mode:
            params["parse_mode"] = parse_mode
        response = requests.post(self._api_url + method, params)
        return response

    def send_sticker(self, chat_id: str, sticker_id: str) -> requests.Response:
        """
        Sends sticker in chat

        :param chat_id: id of destination chat
        :param sticker_id: id of sticker to send
        :return: API response to request
        """
        method = "sendSticker"
        params = {"chat_id": chat_id, "sticker": sticker_id}
        response = requests.post(self._api_url + method, params)
        return response
