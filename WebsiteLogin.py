from configparser import ConfigParser
from pathlib import Path
import requests
import schedule
import time
from bs4 import BeautifulSoup

config_path = (str(Path(__file__).parent.absolute()) + '\\config.ini')
attendance_password = 'Anwesenheit_J1_Asset'
origin_url = 'https://moodle.egkehl.de/'
login_url = 'https://moodle.egkehl.de/moodle/blocks/exa2fa/login/'
attendance_link = 'https://moodle.egkehl.de/moodle/mod/attendance/view.php?id=16845'

def check_config():
    use_config = input('Do you want to use your config? (y/n): ')
    if (use_config.lower() == 'y'):
        return get_config()
    else:
        return set_config()

def set_schedule_task():
    schedule_task = input('Do you want to schedule the task for 8am? (y/n): ')
    if (schedule_task.lower() == 'y'):
        return True
    else:
        return False

def save_config(username, password):
    save_config = input('Do you want to save the config? (y/n): ')
    if (save_config.lower() == 'y'):
        config = ConfigParser()
        config['CONFIG'] = {'username': username, 'password': password}
        config.write(open(config_path, 'w'))

def get_config():
    config = ConfigParser()
    if (Path(config_path).is_file()):
        config.read(config_path)
        if (config.has_section('CONFIG')):
            username = config.get('CONFIG', 'username')
            password = config.get('CONFIG', 'password')
        else:
            password, username = set_config()
        return username, password
    else:
        print('An error occurred while trying reading the config')
        return set_config()

def set_config():
    username = input('Username: ')
    password = input('Password: ')
    save_config(username, password)
    return username, password

def check_login(username, password):
    s = requests.session()

    session_token = s.get(login_url).cookies['MoodleSession']

    headers_login = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'origin': origin_url,
        'referer': login_url
    }
    payload_login = {
        'username': username,
        'password': password,
        'token': session_token
    }
    
    response_login = s.post(login_url, headers=headers_login, data=payload_login)
    if (response_login.status_code != 200):
        print('Failed to login: ' + str(response_login.status_code))
        return
    
    soup = BeautifulSoup(s.get(attendance_link).text, 'html.parser')
    record_attendance = soup.find('td', {'class': 'statuscol cell c2 lastcol'}).findChild('a').get('href')
    print(record_attendance)
    
    split_link = record_attendance.split('?')
    ids = split_link[1].split('&')
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
        'studentpassword': attendance_password,
        'status': '361',
        'sessid': sessid,
        'sesskey': sesskey
    }

    response_attendance = s.post(record_attendance, headers=headers_attendance, data=payload_attendance)
    if (response_attendance.status_code != 200):
        print('Failed to check attendence: ' + str(response_attendance.status_code))
        return
    print('Login successful')

def main():
    try:
        username, password = check_config()
        if (set_schedule_task()):
            schedule.every().day.at('08:00').do(check_login, username, password)
            while True:
                schedule.run_pending()
                time.sleep(30)
        else:
            check_login(username, password)
    except AttributeError:
        print('An error occured while trying to find the attendance-recording link')
        return
    except KeyboardInterrupt:
        print('Script cancelled by user')
        return
    except Exception:
        print('An error occured while trying to run the script')
        return

if (__name__ == '__main__'):
    main()