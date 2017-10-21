#!/usr/bin/env python3
import requests
import requests.cookies

import re

from bs4 import BeautifulSoup

LIBRUS_URL = 'https://synergia.librus.pl'

class Class:
    def __init__(self, weekday, number, name=None, teacher=None, group=None, room=None, free=False):
        self.room = room
        self.group = group
        self.name = name
        self.teacher = teacher
        self.weekday = weekday
        self.number = number
        self.free = free


class_details_re = re.compile(r'^(\s*-\s*)(?P<teacher>.*?)\s*(?P<group>\(.*?\))?\s*(?P<room>s. .*?)$')


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

        r = requests.post(LIBRUS_URL + '/loguj',
                          data=payload, cookies=self.cookies, allow_redirects=False)
        self.cookies = r.cookies
        return r.headers.get('Location') == '/uczen_index'

    def get_timetable(self, week=None):
        url = LIBRUS_URL + '/przegladaj_plan_lekcji'

        html = ''

        if week is None:
            r = requests.get(url, cookies=self.cookies)
            html = r.text
        else:
            payload = {
                "tydzien": week
            }
            r = requests.post(url, cookies=self.cookies, data=payload)
            html = r.text

        soup = BeautifulSoup(html, 'html.parser')

        hours = soup.select('table.plan-lekcji tr.line1')
        schedule = [[None for _ in range(0, 12)] for _ in range(0, 8)]
        for hour_number, hour in enumerate(hours):
            for weekday, single_class in enumerate(hour.select('td')[1:-1]):  # the first and last column is the hour number
                # Extract removes the <b> element from the table cell.
                # We need to do that, because the whole cell is formatted as
                # '<b>class name</b><br/>details', and we want to be able to
                # access the details easily later.
                name_html = single_class.b.extract() if single_class.b is not None else None

                if name_html is None:
                    schedule[weekday][hour_number] = Class(weekday, hour_number, free=True)
                    continue

                # we can just extract the entire text, because the class name was removed earlier.
                name = name_html.text
                details = single_class.text.replace('\xa0', ' ').replace('\n', ' ')
                details_match = class_details_re.match(details)
                if details_match is None:
                    # TODO: zastępstwa
                    continue

                teacher = details_match.group('teacher')
                group = details_match.group('group')
                room = details_match.group('room')
                schedule[weekday][hour_number] = Class(weekday, hour_number,
                                                       name=name,
                                                       teacher=teacher,
                                                       room=room,
                                                       group=group)

        return schedule

s=''
if __name__ == '__main__':
    l = Librus("", "")
    l.login()
    s=l.get_timetable()