import requests

from botslib.errors.BadResponseError import BadResponseError


class BotHandler(object):
    def __init__(self, token: str):
        self._api_url = "https://api.telegram.org/{}/".format(token)
        self._last_offset = None
        self.last_response = None

    def inc_offset(self) -> None:
        if self._last_offset is None:
            self._last_offset = self.last_response["result"][0]["update_id"]
        self._last_offset += 1

    def get_updates_json(self, offset=None, timeout=30) -> dict:
        if offset is None:
            offset = self._last_offset

        method = "getUpdates"
        params = {"offset": offset, "timeout": timeout}
        response = requests.get(self._api_url + method, params)
        self.last_response = response.json()
        return self.last_response

    def get_updates_list(self) -> list:
        if not self.get_updates_json()["ok"]:
            raise BadResponseError
        return self.get_updates_json(self._last_offset)["result"]

    def send_message(self, chat_id: str, message: str, parse_mode=None) -> requests.Response:
        method = "sendMessage"
        params = {"chat_id": chat_id, "text": message}
        if parse_mode:
            params["parse_mode"] = parse_mode
        response = requests.post(self._api_url + method, params)
        return response

    def send_sticker(self, chat_id: str, sticker_id: str) -> requests.Response:
        method = "sendSticker"
        params = {"chat_id": chat_id, "sticker": sticker_id}
        response = requests.post(self._api_url + method, params)
        return response
