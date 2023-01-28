import json

import requests
from requests_oauthlib import OAuth1Session


def retweet(oauth: OAuth1Session, tweet_id):
    url = f"https://api.twitter.com/1.1/statuses/retweet/{tweet_id}.json"
    oauth.post(url)


class FilteredStream:
    def __init__(self, bearer_token, oauth) -> None:
        self._bearer_token = bearer_token
        self._oauth = oauth

    def _bearer_oauth(self, req):
        req.headers["Authorization"] = f"Bearer {self._bearer_token}"
        req.headers["User-Agent"] = "share_nakatani project (test)"
        return req


    def get_rules(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self._bearer_oauth)
        if response.status_code != 200:
            raise Exception("Cannot get rules (HTTP {}): {}".format(
                response.status_code, response.text))
        print(json.dumps(response.json()))
        return response.json()


    def delete_all_rules(self, rules):
        if rules is None or "data" not in rules:
            return None

        ids = list(map(lambda rule: rule["id"], rules["data"]))
        payload = {"delete": {"ids": ids}}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self._bearer_oauth,
            json=payload)
        if response.status_code != 200:
            raise Exception("Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text))
        print(json.dumps(response.json()))


    def set_rules(self):
        rules = [
            {
                "value": "#中谷育 has:images -is:reply -is:retweet",
                "tag": "中谷育"
            },
            {
                "value": "#毎日育ちゃん可愛い大会 has:images -is:reply -is:retweet",
                "tag": "中谷育"
            },
            {
                "value": "#無言で中谷育をあげる見た人もやる has:images -is:reply -is:retweet",
                "tag": "中谷育"
            },
        ]
        payload = {"add": rules}
        response = requests.post(
            "https://api.twitter.com/2/tweets/search/stream/rules",
            auth=self._bearer_oauth,
            json=payload,
        )
        if response.status_code != 201:
            raise Exception("Cannot add rules (HTTP {}): {}".format(
                response.status_code, response.text))
        print(json.dumps(response.json()))


    def stream_with_retweet(self):
        response = requests.get(
            "https://api.twitter.com/2/tweets/search/stream",
            auth=self._bearer_oauth,
            stream=True,
        )
        if response.status_code != 200:
            raise Exception("Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text))
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                print(json.dumps(json_response, indent=4, sort_keys=True))
                retweet(self._oauth, json_response["data"]["id"])


def search_tweets(bearer_oauth, keywords):
    tweet_pool = []
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": "",
        "max_results": 10,
    }

    for keyword in keywords:
        print(f"{keyword}のツイートを検索しています。")
        params["query"] = f"{keyword} -is:reply -is:retweet has:media"
        search_result = requests.get(url, params=params, auth=bearer_oauth)
        if search_result.status_code != 200:
            raise Exception()
        for tweet in reversed(search_result.json()["data"]):
            print(tweet)
            tweet_pool.append(tweet)
    return tweet_pool


def exclude_retweeted(oauth: OAuth1Session, tweet_pool):
    url = "https://api.twitter.com/1.1/statuses/lookup.json"
    tweet_ids = list(set(map(lambda x: x["id"], tweet_pool)))
    params = {"id": ",".join(tweet_ids)}
    res = oauth.get(url, params=params)

    untreated = []
    for tweet in res.json():
        if tweet["retweeted"]:
            continue
        untreated.append(tweet)

    return untreated