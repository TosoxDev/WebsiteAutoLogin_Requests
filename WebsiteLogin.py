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

    headers_login = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'origin': origin_url,
    'referer': login_url
    }
    payload_login = {
        'username': usrname,
        'password': pwd,
        'token': session_token
    }
    
    response_login = s.post(login_url, headers=headers_login, data=payload_login)
    print(response_login.status_code)
    
    soup = BeautifulSoup(s.get(presence_link).text, 'html.parser')
    record_presence = soup.find('td', {"class": "statuscol cell c2 lastcol"}).findChild("a").get('href')
    print(record_presence)
    
    split_link = record_presence.split("?")
    print(split_link)
    ids = split_link[1].split("&amp;")
    sessid = ids[0].replace('sessid=', '')
    sesskey = ids[1].replace('sesskey=', '')
    print(sessid + ', ' + sesskey)
    
    headers_presence = {
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
        'sessid': sessid,
        'sesskey': sesskey
    }

    response_presence = s.post(record_presence, headers=headers_presence, data=payload_presence)
    print(response_presence.status_code)

if (executeNow):
    check_login()
else:
    schedule.every().day.at("08:00").do(check_login)
    while True:
        schedule.run_pending()
        time.sleep(30)
