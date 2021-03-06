import argparse
import logging
import os
import time
import webbrowser
from typing import Optional

import schedule
import spotifier.scopes as S
from spotifier import Spotify
from spotifier.oauth import SpotifyAuthorizationCode

from . import __version__
from .slack import Slack

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s [%(filename)s %(funcName)s]: %(message)s", datefmt="%y/%m/%d %H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def job(slack: Slack, spotify: Spotify) -> Optional[int]:
    track = spotify.get_the_users_currently_playing_track(market="from_token")

    if track is not None and track["is_playing"]:
        item = track["item"]
        # handle exceptions such as podcasts
        if item is None:
            text = ""
            slack.set_status(text=text)
        else:
            name = item.get("name")
            artists = track["item"]["artists"]
            text = f"{name} by {', '.join([artist['name'] for artist in artists])}"
            slack.set_status(text=text)
    else:
        text = ""
        slack.set_status(text=text)

    logger.info(text)

    if track is not None and track["is_playing"] and track["item"] is not None:
        return int((track["item"]["duration_ms"] - track["progress_ms"]) / 1000)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--continuous", action="store_true", help="Set next update schedule dynamically")
    parser.add_argument("-e", "--emoji", default=":musical_note:", help="Emoji for Slack status")
    parser.add_argument("-i", "--interval", default=3, type=int, help="Interval (min) to hit API in the normal mode")
    parser.add_argument("-v", "--version", action="store_true", help="Show version")
    args = parser.parse_args()

    if args.version:
        print("Spock v{}".format(__version__))
        return

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

    slack = Slack(os.environ["SLACK_ACCESS_TOKEN"], emoji=args.emoji)
    spotify = Spotify(oauth, auto_refresh=True)

    if args.continuous:
        while True:
            remaining = job(slack, spotify)
            if remaining is None:
                time.sleep(args.interval * 60)  # if not playing, next update is args.interval sec after
            else:
                time.sleep(remaining + 1)  # add extra 1 sec
    else:
        schedule.every(args.interval).minutes.do(job, slack, spotify)
        while True:
            schedule.run_pending()
