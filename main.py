import os
import sys
import time
import traceback
import random
from pathlib import Path
from threading import Thread

from flask import Flask
from urllib3.exceptions import ProtocolError
from requests_oauthlib import OAuth1Session

from twitterapi import (FilteredStream, search_tweets, exclude_retweeted,
                        retweet)

from notify import (
    ConsoleSubscriber,
    FileSubscriber,
    ErrorPublisher,
)

app = Flask(__name__)


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

error_pub = ErrorPublisher()
error_pub.subscribe(ConsoleSubscriber())
error_pub.subscribe(FileSubscriber("log.txt"))

oauth = OAuth1Session(api_key, api_secret_key, access_token,
                    access_token_secret)


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "share_nakatani project (test)"
    return r


def re_retweet():
    keywords = ["#毎日育ちゃん可愛い大会", "#無言で中谷育をあげる見た人もやる", "#中谷育"]
    tweet_pool = search_tweets(bearer_oauth, keywords)
    untreated = exclude_retweeted(oauth, tweet_pool)
    for untreated_tweet in untreated:
        retweet(oauth, untreated_tweet["id"])
        print("EXEC(RT):", untreated_tweet["id"])
        time.sleep(random.randint(1, 3))


def main():
    re_retweet()
    running = True
    print("ストリーミングを開始します。")
    stream = FilteredStream(bearer_token, oauth)
    error_pub.notify("Started streaming.")
    rate_limit = 50
    while running:
        try:
            if rate_limit == 0:
                running = False
                error_pub.notify("LATE LIMIT!")
                time.sleep(3 * 60)
            rate_limit = stream.stream_with_retweet(notify=error_pub.notify)
        except ProtocolError:
            rate_limit -= 1
            error_pub.notify(f"ProtocolError!\n{str(traceback.format_exc())}")
            minute = random.randint(1, 2)
            time.sleep(minute * 60)
            re_retweet()
        except Exception:
            rate_limit -= 1
            error_pub.notify(f"Exception!\n{str(traceback.format_exc())}")
            minute = random.randint(1, 2)
            time.sleep(minute * 60)
            re_retweet()


if __name__ == "__main__":
    keep_alive()
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
        except Exception:
            error_pub.notify(f"Outer Exception!\n{str(traceback.format_exc())}")
            time.sleep(3 * 60)
