# config.py
import datetime


class Config:
    # 初始的登录和默认预约信息
    LOGIN_DATA = {
        'dlm': '22011207',
        'mm': '040019',
        'yzm': '1',
        'logintype': 'sno',
        'continueurl': '',
        'openid': ''
    }

    # 默认预约信息，后续用户交互时会动态修改
    BOOKING_DATA = {
        'serviceid': '',  # 场馆类型
        'users': '',  # 随行人员
        'date': '',         # 用户输入日期
        'time_slot': '',    # 用户选择时间段
        'venue_id': '',     # 用户选择场馆
        'stockid': '',      # 用户选择库存ID
        'stockdetail_id': '' # 用户选择场馆的详细库存ID
    }

    # 基础 URL
    BASE_URL = 'http://order.njmu.edu.cn:8088'

    # 预约时间规则
    BOOKING_HOURS = (8, 23)  # 允许预约的时间段

    # 自动任务定时器
    SCHEDULE_TIME = "08:00"  # 定时任务执行时间，每天8:00执行

    @staticmethod
    def is_booking_time():
        """判断当前时间是否在允许的预约时间段内"""
        now = datetime.datetime.now().time()
        start_time = datetime.time(Config.BOOKING_HOURS[0], 0)
        end_time = datetime.time(Config.BOOKING_HOURS[1], 0)
        return start_time <= now <= end_time