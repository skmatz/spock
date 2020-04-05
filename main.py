import json
import os
import webbrowser
import logging

import requests
import schedule

import spotifier.scopes as S
from spotifier import Spotify
from spotifier.oauth import SpotifyAuthorizationCode

INTERVAL = 3  # minutes

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def job(slack: Slack, spotify: Spotify):
    track = spotify.get_the_users_currently_playing_track(market="from_token")

    if track is not None:
        name = track["item"]["name"]
        artists = track["item"]["artists"]
        text = f"{name} by {', '.join([artist['name'] for artist in artists])}"
        slack.set_status(text=text)
    else:
        text = ""
        slack.set_status(text="")

    logger.info(text)


def main():
    oauth = SpotifyAuthorizationCode(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri=os.environ["SPOTIFY_REDIRECT_URI"],
        scopes=[S.USER_READ_CURRENTLY_PLAYING],
    )

    webbrowser.open(oauth.get_authorize_url())
    url = input("Input redirected URL: ")

    code = oauth.parse_response_code(url)
    oauth.set_token(code)

    slack = Slack(os.environ["SLACK_ACCESS_TOKEN"], emoji=":spotify:")
    spotify = Spotify(oauth, auto_refresh=True)

    schedule.every(INTERVAL).minutes.do(job, slack, spotify)

    while True:
        schedule.run_pending()


if __name__ == "__main__":
    main()
