from config import Config
from order.book import Booking


def setup_config():
    """提前设置预约参数"""
    print("请设置预约信息:")

    # 输入预约日期
    # date = input("请输入预约日期 (格式: YYYY-MM-DD): ")
    date = '2024-09-27'
    Config.BOOKING_DATA['date'] = date

    # 输入场馆类型
    # serviceid = input("请输入场馆类型 (serviceid): ")
    serviceid = '22'
    Config.BOOKING_DATA['serviceid'] = serviceid

    # 输入预约时间段
    # time_slot = input("请输入预约时间段 (格式: HH:MM-HH:MM): ")
    time_slot = '20:01-21:00'
    Config.BOOKING_DATA['time_slot'] = time_slot

    # 输入场地编号
    # stockid = input("请输入场地编号 (stockid): ")
    stockid = '10382'
    Config.BOOKING_DATA['stockid'] = stockid

    # 输入详细的 stockdetail_id
    # stockdetail_id = input("请输入场地详细 ID (stockdetail_id): ")
    stockdetail_id = '144995'
    Config.BOOKING_DATA['stockdetail_id'] = stockdetail_id

    # 输入随行人员的 ID
    # users = input("请输入随行人员的 ID (多个 ID 用逗号分隔): ")
    users = '160734'
    Config.BOOKING_DATA['users'] = users

    # 打印设置好的参数
    # print("\n已设置的预约参数:")
    # for key, value in Config.BOOKING_DATA.items():
    #     print(f"{key}: {value}")

    print("\n配置已完成，scheduler 将在预约时间内自动执行预约任务。")

if __name__ == "__main__":
    setup_config()
    Booking.book_venue()