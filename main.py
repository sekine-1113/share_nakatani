import os
import sys
from pathlib import Path
from threading import Thread

from flask import Flask
from requests_oauthlib import OAuth1Session

from share_nktn.twitterapi import FilteredStream
from share_nktn.notify import ErrorPublisher, LINESubscriber


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


def main():
    error = ErrorPublisher()
    error.subscribe(LINESubscriber(line_bearer_token))

    running = True
    print("ストリーミングを開始します。")
    stream = FilteredStream(bearer_token, oauth)

    while running:
        try:
            stream.stream_with_retweet()
        except Exception as e:
            print(e)
            error.notify(str(e))
            running = False


if __name__ == "__main__":
    keep_alive()
    main()
