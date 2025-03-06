# book.py
import json

import requests
from urllib.parse import urlencode
from config import Config
from login import Login

global cnt
cnt = 0
BASE_URL = 'http://order.njmu.edu.cn:8088'

class Booking:
    def __init__(self, stockid='', serviceid='', id='', users='', username='', password=''):
        self.stockid = stockid
        self.serviceid = serviceid
        self.id = id
        self.users = users
        self.username = username
        self.password = password
        if username and password:
            login = Login(username, password)
            self.session = login.pre_login()
            self.book_url = f"{BASE_URL}/cgyd/order/tobook.html"
            self.payload = {
                "param": {
                    "stockdetail": {str(self.stockid): str(self.id)},
                    "serviceid": self.serviceid,
                    "stockid": f"{self.stockid},",
                    "remark": "",
                    "users": self.users
                },
                "num": 1,
                "json": True
            }

            # 将 payload 字典转换为 URL 编码的字符串
            self.encoded_payload = urlencode({
                "param": json.dumps(self.payload["param"]),
                "num": self.payload["num"],
                "json": self.payload["json"]
            })

            self.headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{BASE_URL}/cgyd/product/show.html?id={self.serviceid}"
            }

    def pre_book(self):
        global cnt
        if cnt == 50:
            return
        # 准备预约请求数据 (将其 URL 编码)

        # 发送预约请求
        response = self.session.post(self.book_url, data=self.encoded_payload, headers=self.headers)
        # 处理响应
        if response.status_code == 200:
            try:
                result = response.json()
            except Exception as e:
                print("fail to convert!")
                print(response.content.decode('utf-8'))
                cnt += 1
                self.pre_book()
                raise e
            if result['result'] == '1':
                print("预约成功！")
                print(result['message'])
            elif '未到该日期的预订时间' in result['message']:
                print(f"预约失败：{result['message']}")
                cnt += 1
                self.pre_book()
            elif '每日限预约一场' in result['message']:
                print(f"预约失败：{result['message']}")
            else:
                print(f"其他错误：{result['message']}")
                cnt += 1
                self.pre_book()
        else:
            print(f"请求失败，状态码: {response.status_code}")
            cnt += 1
            self.pre_book()


    @staticmethod
    def book_venue():
        global cnt
        if cnt==5:
            return
        session = Login.get_session()
        # 准备预约请求数据 (将其 URL 编码)
        book_url = f"{Config.BASE_URL}/cgyd/order/tobook.html"
        payload = {
            "param": {
                "stockdetail": {str(Config.BOOKING_DATA['stockid']): str(Config.BOOKING_DATA['stockdetail_id'])},
                "serviceid": Config.BOOKING_DATA['serviceid'],
                "stockid": f"{Config.BOOKING_DATA['stockid']},",
                "remark": "",
                "users": Config.BOOKING_DATA['users']
            },
            "num": 1,
            "json": True
        }

        # 将 payload 字典转换为 URL 编码的字符串
        encoded_payload = urlencode({
            "param": json.dumps(payload["param"]),
            "num": payload["num"],
            "json": payload["json"]
        })

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"{Config.BASE_URL}/cgyd/product/show.html?id={Config.BOOKING_DATA['serviceid']}"
        }

        # 发送预约请求
        response = session.post(book_url, data=encoded_payload, headers=headers)
        # 处理响应
        if response.status_code == 200:
            result = response.json()
            if result['result'] == '1':
                print("预约成功！")
                print(result['message'])
            elif '未到该日期的预订时间' in result['message']:
                print(f"预约失败：{result['message']}")
                cnt += 1
                Booking.book_venue()
            elif '每日限预约一场' in result['message']:
                print(f"预约失败：{result['message']}")
            else:
                print(f"其他错误：{result['message']}")
        else:
            print(f"请求失败，状态码: {response.status_code}")

if __name__ == '__main__':
    Booking.book_venue()
