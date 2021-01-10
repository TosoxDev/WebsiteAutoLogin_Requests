import requests
import schedule
import time
from bs4 import BeautifulSoup

usrname = 'username'
pwd = 'password'

URL = 'https://moodle.egkehl.de/'
LOGIN_ROUTE = 'moodle/blocks/exa2fa/login/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'origin': URL,
    'referer': URL + LOGIN_ROUTE
}

def check_login():
    s = requests.session()
    session_token = s.get(URL + LOGIN_ROUTE).cookies['MoodleSession']
    payload = {
        'username': usrname,
        'password': pwd,
        'token': session_token
    }
    
    response = s.post(URL + LOGIN_ROUTE, headers=HEADERS, data=payload)
    print(response.status_code)

    soup = BeautifulSoup(s.get(URL + 'moodle').text, 'html.parser')
    deutsch_kurs = soup.find('a', id='label_3_22').get('href')
    print(deutsch_kurs)
    
    soup = BeautifulSoup(s.get(deutsch_kurs).text, 'html.parser')
    anwesenheit = soup.find('li', id='section-1').findChild("a").get('href')
    print(anwesenheit)

    soup = BeautifulSoup(s.get(anwesenheit).text, 'html.parser')

schedule.every().day.at("18:08").do(check_login)

while True:
    schedule.run_pending()
    time.sleep(30)
