import requests
import schedule
import time
from bs4 import BeautifulSoup

#config start
usrname = 'username'
pwd = 'password'
presence_password = 'Anwesenheit_J1_Asset'
origin_url = 'https://moodle.egkehl.de/'
login_url = 'https://moodle.egkehl.de/moodle/blocks/exa2fa/login/'
presence_link = 'https://moodle.egkehl.de/moodle/mod/attendance/view.php?id=16845'
executeNow = True
#config end

def check_login():
    s = requests.session()
    session_token = s.get(login_url).cookies['MoodleSession']

    HEADERS_LOGIN = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'origin': origin_url,
    'referer': login_url
    }
    payload_login = {
        'username': usrname,
        'password': pwd,
        'token': session_token
    }
    
    response_login = s.post(login_url, headers=HEADERS_LOGIN, data=payload_login)
    print(response_login.status_code)
    
    soup = BeautifulSoup(s.get(presence_link).text, 'html.parser')
    record_presence = soup.find('td', {"class": "statuscol cell c2 lastcol"}).findChild("a").get('href')
    print(record_presence)

    soup = BeautifulSoup(s.get(record_presence).text, 'html.parser')
    
    link = record_presence
    split_link = link.split("?")
    print(split_link)
    ids = split_link[1].split("&amp;")
    print(ids)
    
    HEADERS_PRESENCE = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'origin': origin_url,
    'referer' : record_presence
    }
    payload_presence = {
        '_qf__mod_attendance_form_studentattendance': '1',
        'mform_isexpanded_id_session=1': '1',
        'studentpassword': presence_password,
        'status': '361',
        'submitbutton': 'Änderungen speichern',
        'sessid': ids[0],
        'sesskey': ids[1]
    }

    response_presence = s.post(record_presence, headers=HEADERS_PRESENCE, data=payload_presence)
    print(response_presence.status_code)

if (executeNow):
    check_login()
else:
    schedule.every().day.at("08:00").do(check_login)
    while True:
        schedule.run_pending()
        time.sleep(30)
