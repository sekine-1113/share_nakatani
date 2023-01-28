import os
import time
import random
import datetime
from threading import Thread

from flask import Flask
from requests_oauthlib import OAuth1Session
from apscheduler.schedulers.blocking import BlockingScheduler

from .twitterapi import retweet, search_tweets, exclude_retweeted

scheduler = BlockingScheduler()

bearer_token = os.environ.get("BEARER")
api_key = os.environ.get("API_KEY")
api_secret_key = os.environ.get("API_SECRET_KEY")
access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

oauth = OAuth1Session(api_key, api_secret_key, access_token,
                    access_token_secret)

app = Flask(__name__)


@app.route("/")
def index():
    return f"bot is running! {datetime.datetime.now()}"


def run():
    app.run("0.0.0.0", port=8080)


def keep_alive():
    Thread(target=run).start()


def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "share_nakatani project (test)"
    return r


@scheduler.scheduled_job('interval', minutes=30)
def main():
    keywords = ["#毎日育ちゃん可愛い大会", "#無言で中谷育をあげる見た人もやる", "#中谷育"]
    tweet_pool = search_tweets(bearer_oauth, keywords)
    untreated = exclude_retweeted(oauth, tweet_pool)
    for untreated_tweet in untreated:
        retweet(oauth, untreated_tweet["id"])
        print("EXEC(RT):", untreated_tweet["id"])
        time.sleep(random.randint(1, 3))


if __name__ == "__main__":
    keep_alive()
    try:
        scheduler.start()
    except Exception as e:
        print(e)
