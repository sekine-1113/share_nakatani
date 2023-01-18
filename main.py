import datetime
import os
import time
from random import choice, randint

import requests
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv


def get_bearer(API_key, API_secret_key):
    url = "https://api.twitter.com/oauth2/token"
    data = {"grant_type" : "client_credentials"}
    headers = {"Content-Type" : "application/x-www-form-urlencoded;charset=UTF-8"}
    request = requests.post(
                    url,
                    data=data,
                    headers=headers,
                    auth=(API_key, API_secret_key)
                )
    if request.status_code != 200:
        return request
    return request.json()["access_token"]

def retweet(oauth, tweet_id):
    url = f"https://api.twitter.com/1.1/statuses/retweet/{tweet_id}.json"
    oauth.post(url)


load_dotenv()
API_KEY = os.environ["API_KEY"]
API_SEC_KEY = os.environ["API_SEC"]
ACC_TOKEN = os.environ["TOKEN"]
ACC_SEC_TOKEN = os.environ["TOKEN_SEC"]


def main():
    url = "https://api.twitter.com/2/tweets/search/recent"
    today = datetime.date.today()
    now_year = today.year
    birth = datetime.date(now_year, 12, 16)
    keywords = [
        "#毎日育ちゃん可愛い大会",
        ["#中谷育誕生祭"+str(now_year), "#中谷育生誕祭"+str(now_year)]
    ][today == birth]
    if today == birth:
        keywords = choice(keywords)
    query = f"{keywords} -is:reply -is:retweet has:media"

    params = {
        "query" : query,
        "max_results" : 10,
        "tweet.fields" : "id,referenced_tweets"
    }
    BEARER = get_bearer(API_KEY, API_SEC_KEY)
    req = requests.get(url, params=params, headers={"Authorization":f"Bearer {BEARER}"})
    if req.status_code != 200:
        exit(req.status_code)

    OAUTH = OAuth1Session(API_KEY, API_SEC_KEY, ACC_TOKEN, ACC_SEC_TOKEN)
    for res in reversed(req.json()["data"]):
        print(res)
        retweet(OAUTH, res["id"])
        time.sleep(randint(15,45))


if __name__ == "__main__":
    main()

