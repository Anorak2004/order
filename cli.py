import json
import os
from fetch_data import FetchData
from config import Config
from book import Booking


def prompt_for_date_and_serviceid():
    """提示用户输入日期和 serviceid"""
    date = input("请输入希望预约的日期 (格式: YYYY-MM-DD): ")
    serviceid = input("请输入场馆类型的 serviceid: ")
    return date, serviceid


def display_options(data):
    """展示场馆信息供用户选择"""
    for idx, item in enumerate(data):
        venue_name = item.get('sname', 'N/A')
        time_no = item['stock'].get('time_no', 'N/A')
        stockid = item.get('stockid', 'N/A')
        print(f"{idx}. 场馆: {venue_name}, 时间: {time_no}, stockid: {stockid}")
    return len(data)


def get_user_choice(prompt, total_options):
    """获取用户的选择，限制在选项范围内"""
    while True:
        try:
            choice = int(input(prompt))
            if 0 <= choice < total_options:
                return choice
            else:
                print(f"请输入一个 0 到 {total_options - 1} 之间的数字")
        except ValueError:
            print("无效输入，请输入数字")


def run_cli():
    date, serviceid = prompt_for_date_and_serviceid()

    # 尝试加载本地已有的 JSON 数据
    data = FetchData.load_data_from_json(date, serviceid)

    # 如果没有数据，则尝试在线获取
    if data is None:
        print(f"没有找到 {date} 的数据，正在获取...")
        data = FetchData.fetch_service_data(date, serviceid)
        if data:
            FetchData.save_data_to_json(data, date, serviceid)
        else:
            print("无法获取数据，程序终止。")
            return

    # 展示获取到的场馆信息并让用户选择
    total_options = display_options(data)
    choice = get_user_choice("请选择一个场馆: ", total_options)

    selected_venue = data[choice]
    selected_stockid = selected_venue['stockid']
    selected_time_no = selected_venue['stock']['time_no']
    selected_venue_name = selected_venue['sname']

    print(f"你选择了 {selected_venue_name}，时间: {selected_time_no}")

    # 选择随行人员
    users = input("请输入随行人员的 ID (多个ID用逗号分隔): eg.160747/160734")

    # 更新配置
    Config.BOOKING_DATA['stockid'] = selected_stockid
    Config.BOOKING_DATA['stockdetail_id'] = selected_venue['id']
    Config.BOOKING_DATA['date'] = date
    Config.BOOKING_DATA['time_slot'] = selected_time_no
    Config.BOOKING_DATA['users'] = users
    Config.BOOKING_DATA['serviceid'] = serviceid

    # 发起预约
    Booking.book_venue()


if __name__ == "__main__":
    run_cli()
