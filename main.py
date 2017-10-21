#!/usr/bin/env python3
import requests
import requests.cookies


class Librus:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookies = requests.cookies.RequestsCookieJar();
        self.cookies.set("TestCookie", "1")

    def login(self):
        payload = {
            "login": self.username,
            "passwd": self.password,
            "czy_js": 1
        }

        r = requests.post('https://synergia.librus.pl/loguj', data=payload, cookies=self.cookies, allow_redirects=False)
        return r.headers.get('Location') == '/uczen_index'


if __name__ == '__main__':
    l = Librus("", "")
    print(l.login())
    print(l.cookies)
