import json

import requests


class Slack:
    USERS_PROFILE_SET_ENDPOINT = "https://slack.com/api/users.profile.set"

    def __init__(self, token: str, emoji: str = ":musical_note:"):
        self._token = token
        self._emoji = emoji

    def set_status(self, text: str):
        payload = {
            "token": self._token,
            "profile": json.dumps({"status_text": text, "status_emoji": self._emoji}),
        }

        _ = requests.post(self.USERS_PROFILE_SET_ENDPOINT, data=payload)
