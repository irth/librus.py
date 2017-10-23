#!/usr/bin/env python3
import requests
import requests.cookies

import re

from bs4 import BeautifulSoup

LIBRUS_URL = 'https://synergia.librus.pl'

class Class:
    def __init__(self, weekday, number, name=None, teacher=None, substitute_teacher=False, group=None, room=None):
        self.substitute_teacher = substitute_teacher
        self.room = room
        self.group = group
        self.name = name
        self.teacher = teacher
        self.weekday = weekday
        self.number = number


class_details_re = re.compile(r'^(\s*-\s*)(?P<teacher>.*?)\s*(?P<group>\(.*?\))?\s*(?P<room>s\. .*)?$')


class Librus:
    def __init__(self, username=None, password=None, cookie=None):
        self.username = username
        self.password = password
        self.cookies = requests.cookies.RequestsCookieJar();
        self.cookies.set('TestCookie', '1')
        if cookie is not None:
            self.cookies.set('DZIENNIKSID', cookie)

    def login(self):
        payload = {
            'login': self.username,
            'passwd': self.password,
            'czy_js': 1
        }

        r = requests.post(LIBRUS_URL + '/loguj',
                          data=payload, cookies=self.cookies, allow_redirects=False)
        self.cookies = r.cookies
        return r.cookies.get('DZIENNIKSID') if r.headers.get('Location') == '/uczen_index' else None

    def get_timetable(self, week=None):
        url = LIBRUS_URL + '/przegladaj_plan_lekcji'

        html = ''

        if week is None:
            r = requests.get(url, cookies=self.cookies)
            html = r.text
        else:
            payload = {
                'tydzien': week
            }
            r = requests.post(url, cookies=self.cookies, data=payload)
            html = r.text

        soup = BeautifulSoup(html, 'html.parser')

        hours = soup.select('table.plan-lekcji tr.line1')
        schedule = [[None for _ in range(0, 12)] for _ in range(0, 7)]
        for hour_number, hour in enumerate(hours):
            for weekday, single_class in enumerate(hour.select('td')[1:-1]):  # the first and last column is the hour number
                substitute_teacher = False
                if single_class.a is not None and single_class.a.text.strip() == 'zastępstwo':
                    # Read the next comment below to see what extract does
                    single_class.a.extract()
                    substitute_teacher = True

                # Extract removes the <b> element from the table cell.
                # We need to do that, because the whole cell is formatted as
                # '<b>class name</b><br/>details', and we want to be able to
                # access the details easily later.
                name_html = single_class.b.extract() if single_class.b is not None else None

                if name_html is None:
                    schedule[weekday][hour_number] = None  # no class
                    continue

                # we can just extract the entire text, because the class name was removed earlier.
                name = name_html.text
                details = single_class.text.replace('\xa0', ' ').replace('\n', ' ').strip()
                details_match = class_details_re.match(details)

                teacher = group = room = None
                if details_match is not None:
                    teacher = details_match.group('teacher')
                    group = details_match.group('group')
                    room = details_match.group('room')

                schedule[weekday][hour_number] = Class(weekday, hour_number,
                                                       name=name,
                                                       teacher=teacher,
                                                       substitute_teacher=substitute_teacher,
                                                       room=room,
                                                       group=group)
        return schedule

s=''
if __name__ == '__main__':
    l = Librus('', '')
    l.login()
    s=l.get_timetable()