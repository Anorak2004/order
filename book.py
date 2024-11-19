# E:\WorkSpace\js\order\book.py
# Booking module for making venue reservations.
from urllib.parse import urlencode
import json
import requests
from login import Login
from config import Config
from fetch_data import FetchData

class Booking:
    def __init__(self, date, serviceid, venue_index=0, users='', username='', password=''):
        self.users = users
        self.username = username
        self.password = password
        self.max_attempts = 50
        self.attempts = 0

        # Prepare booking parameters using fetch_data module
        booking_params = FetchData.prepare_booking_params(date, serviceid, venue_index)
        self.stockid = booking_params['stockid']
        self.id = booking_params['id']
        self.serviceid = booking_params['serviceid']
        self.sname = booking_params['sname']
        self.s_date = booking_params['s_date']
        self.time_no = booking_params['time_no']

        if username and password:
            login = Login(username, password)
            self.session = login.pre_login()
            self.book_url = f"{Config.BASE_URL}/cgyd/order/tobook.html"
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
            self.encoded_payload = urlencode({
                "param": json.dumps(self.payload["param"]),
                "num": self.payload["num"],
                "json": self.payload["json"]
            })
            self.headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": f"{Config.BASE_URL}/cgyd/product/show.html?id={self.serviceid}"
            }

    def pre_book(self):
        while self.attempts < self.max_attempts:
            response = self.session.post(self.book_url, data=self.encoded_payload, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result['result'] == '1':
                    print(f"Booking successful for {self.sname} on {self.s_date} during {self.time_no}!")
                    print(result['message'])
                    break
                elif '未到该日期的预订时间' in result['message']:
                    print(f"Booking failed: {result['message']}, retrying...")
                    self.attempts += 1
                elif '每日限预约一场' in result['message']:
                    print(f"Booking failed: {result['message']}")
                    break
                else:
                    print(f"Other error: {result['message']}")
                    break
            else:
                print(f"Request failed, status code: {response.status_code}")
                break
