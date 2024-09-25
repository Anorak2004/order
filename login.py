# login.py
import requests
from config import Config

class Login:
    @staticmethod
    def get_session():
        login_url = f"{Config.BASE_URL}/cgyd/login.html"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        # 发送登录请求
        session = requests.Session()
        response = session.post(login_url, data=Config.LOGIN_DATA, headers=headers)
        if response.status_code == 200:
            print("登录成功，获取 session")
            return session
        else:
            raise Exception("登录失败")

if __name__ == '__main__':
    session = Login.get_session()
    print(f"Session: {session.cookies}")
