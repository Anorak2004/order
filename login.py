# login.py
import requests
from config import Config
from fastapi import HTTPException
from sqlalchemy.orm import Session


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
        # 发送登录请求
        session = requests.Session()
        response = session.post(login_url, data=self.login_data, headers=headers)
        if response.status_code == 200:
            print("登录成功，获取 session")
            url = 'http://order.njmu.edu.cn:8088/cgyd/product/show.html?id=22'
            session.get(url)
            return session
        else:
            raise Exception("登录失败")

    class LoginService:
        def __init__(self, db: Session):
            self.db = db
            
        async def authenticate(self, username: str, password: str):
            """统一认证入口"""
            session = requests.Session()
            response = session.post(login_url, data=Config.LOGIN_DATA, headers=headers)
            if response.status_code == 200:
                print("登录成功，获取 session")
                url = 'http://order.njmu.edu.cn:8088/cgyd/product/show.html?id=22'
                session.get(url)
                
                # 记录登录日志
                self.db.add(LoginLog(
                    username=username,
                    login_time=datetime.now()
                ))
                self.db.commit()
                return session
            else:
                raise Exception("登录失败")

    # 废弃原静态方法，全部改为实例方法调用


if __name__ == '__main__':
    session = Login.get_session()
    print(f"Session: {session.cookies}")
