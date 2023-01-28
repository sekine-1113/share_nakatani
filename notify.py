import time
from abc import ABC, abstractmethod

import requests


class IPubulisher:
    def __init__(self) -> None:
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)
        return self

    def unsubscribe(self, subscriber):
        self.subscribers.remove(subscriber)
        return self

    def notify(self, message):
        for subscriber in self.subscribers:
            subscriber.update(message)


class ErrorPublisher(IPubulisher):
    pass


class ISubscriber(ABC):
    @abstractmethod
    def update(self, message):
        print(message)


class LINESubscriber(ISubscriber):

    def __init__(self, token) -> None:
        super().__init__()
        self._token = token

    def update(self, message):
        endpoint = "https://notify-api.line.me/api/notify"
        payload = {"message" : message}
        headers = {"Authorization": "Bearer "+ self._token}
        requests.post(endpoint, data=payload, headers=headers)

    def check_remaining(self) -> int:
        endpoint = "https://notify-api.line.me/api/status"
        headers = {"Authorization": "Bearer "+ self._token}
        req = requests.get(endpoint, headers=headers)
        img_remaining = int(req.headers["X-RateLimit-ImageRemaining"])
        return img_remaining

    def sleep(self):
        endpoint = "https://notify-api.line.me/api/status"
        headers = {"Authorization": "Bearer "+ self._token}
        req = requests.get(endpoint, headers=headers)
        reset_time = int(req.headers["X-RateLimit-Reset"])
        sleep_time = reset_time - int(time.time())
        print(f"{sleep_time}秒sleepします...")
        for i in range(sleep_time):
            print("\r{:5d} / {:5d}".format(i, sleep_time), end="")
            time.sleep(1)