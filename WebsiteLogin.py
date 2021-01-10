import requests
import schedule
import time

def check_login():
    s = requests.session()
    payload = {
        'username': 'username',
        'password': 'password'
    }
    response = s.post("https://moodle.egkehl.de/moodle/blocks/exa2fa/login/", data=payload)
    print(response.status_code)

schedule.every().day.at("08:00").do(check_login)

while True:
    schedule.run_pending()
    time.sleep(30)
