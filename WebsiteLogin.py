import requests
import schedule
import time
from bs4 import BeautifulSoup

usrname = input('Username: ')
pwd = input('Password: ')
schedule_task = input('Do you want to schedule the task for 8am? (y/n): ')

attendance_password = 'Anwesenheit_J1_Asset'
origin_url = 'https://moodle.egkehl.de/'
login_url = 'https://moodle.egkehl.de/moodle/blocks/exa2fa/login/'
attendance_link = 'https://moodle.egkehl.de/moodle/mod/attendance/view.php?id=16845'

def should_schedule_task():
    if (schedule_task.lower() == 'y'):
        return True
    else:
        return False

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
    if (response_login.status_code != 200):
        print('Failed to login: ' + str(response_login.status_code))
        return
    
    try:
        soup = BeautifulSoup(s.get(attendance_link).text, 'html.parser')
        record_attendance = soup.find('td', {'class': 'statuscol cell c2 lastcol'}).findChild('a').get('href')
        print(record_attendance)
    except Exception:
        print('Error finding the attendance-recording link')
        return
    
    split_link = record_attendance.split('?')
    print(split_link)
    ids = split_link[1].split('&amp;')
    sessid = ids[0].replace('sessid=', '')
    sesskey = ids[1].replace('sesskey=', '')
    print(str(sessid) + ', ' + str(sesskey))
    
    headers_attendance = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'origin': origin_url,
    'referer' : record_attendance
    }
    payload_attendance = {
        '_qf__mod_attendance_form_studentattendance': '1',
        'mform_isexpanded_id_session=1': '1',
        'studentpassword': attendance_password,
        'status': '361',
        'submitbutton': 'Änderungen speichern',
        'sessid': sessid,
        'sesskey': sesskey
    }

    response_attendance = s.post(record_attendance, headers=headers_attendance, data=payload_attendance)
    if (response_attendance.status_code != 200):
        print('Failed to check attendence: ' + str(response_attendance.status_code))
        return

if (should_schedule_task()):
    schedule.every().day.at('08:00').do(check_login)
    while True:
        schedule.run_pending()
        time.sleep(30)
else:
    check_login()

