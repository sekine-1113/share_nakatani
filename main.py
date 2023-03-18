import os
import sys
import time
import random
from pathlib import Path
from threading import Thread

from flask import Flask
from requests_oauthlib import OAuth1Session
from urllib3.exceptions import ProtocolError

from notify import ErrorPublisher, LINESubscriber, ConsoleSubscriber
from twitterapi import (
    FilteredStream,
    _bearer_oauth,
    exclude_retweeted,
    retweet,
    search_tweets
)


app = Flask("")

@app.route("/")
def index():
    import datetime
    return f"bot is running! {datetime.datetime.now()}"

def run():
    app.run("0.0.0.0", port=8080)

def keep_alive():
    Thread(target=run).start()


root = Path(sys.argv[0]).parent
env_file = root / ".env"

if env_file.exists():
    import dotenv
    dotenv.load_dotenv(env_file)

if os.environ.get("BEARER") is None:
    raise Exception()

bearer_token = os.environ.get("BEARER")
api_key = os.environ.get("API_KEY")
api_secret_key = os.environ.get("API_SECRET_KEY")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
line_bearer_token = os.environ.get("LINE_BEARER")

oauth = OAuth1Session(api_key, api_secret_key, access_token, access_token_secret)


def back_tracking():
    keywords = ["#毎日育ちゃん可愛い大会", "#無言で中谷育をあげる見た人もやる", "#中谷育"]
    tweet_pool = search_tweets(
        bearer_oauth=lambda r: _bearer_oauth(r, bearer_token),
        keywords=keywords
    )
    untreated = exclude_retweeted(oauth, tweet_pool)
    for untreated_tweet in untreated:
        retweet(oauth, untreated_tweet["id"])
        print("EXEC(RT):", untreated_tweet["id"])
        time.sleep(random.randint(1, 3))


def main():
    error = ErrorPublisher()
    error.subscribe(LINESubscriber(line_bearer_token))
    error.subscribe(ConsoleSubscriber())


    print("ストリーミングを開始します。")
    stream = FilteredStream(bearer_token, oauth)
    running = True
    while running:
        try:
            stream.stream_with_retweet()
        except ProtocolError as e:
            error.notify(str(e))
            time.sleep(300)
            back_tracking()
        except Exception as e:
            error.notify(str(e))
            time.sleep(300)
            back_tracking()


if __name__ == "__main__":
    keep_alive()
    main()
