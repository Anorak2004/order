import schedule
import time
from book import Booking
from config import Config
from config_setup import setup_config

def check_booking_conditions():
    """判断是否在可预约时间内并执行预约"""
    if Config.is_booking_time():
        print("当前时间在可预约时间段内，开始执行预约流程...")
        Booking.book_venue()  # 直接调用预约函数
    else:
        print(f"当前时间不在预约时间段内（{Config.BOOKING_HOURS[0]}:00 - {Config.BOOKING_HOURS[1]}:00）")

def start_scheduler():
    """启动定时任务，每天在设定的时间运行"""
    schedule_time = Config.SCHEDULE_TIME
    print(f"设置定时任务，每天 {schedule_time} 执行")
    schedule.every().day.at(schedule_time).do(check_booking_conditions)

    while True:
        schedule.run_pending()
        time.sleep(1)  # 每60秒检查一次任务是否需要执行

if __name__ == "__main__":
    setup_config()
    start_scheduler()
