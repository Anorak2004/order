# E:\WorkSpace\js\order\login.py
# Login module to authenticate and get a session.
import requests
from config import Config

class Login:
    def __init__(self, username='', password=''):
        self.username = username
        self.password = password
        self.login_data = {
            'dlm': str(self.username),
            'mm': str(self.password),
            'yzm': '1',
            'logintype': 'sno',
            'continueurl': '',
            'openid': ''
        }

    def pre_login(self):
        login_url = f"{Config.BASE_URL}/cgyd/login.html"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        session = requests.Session()
        response = session.post(login_url, data=self.login_data, headers=headers)
        if response.status_code == 200:
            print("Login successful, session obtained")
            return session
        else:
            raise Exception("Login failed")
