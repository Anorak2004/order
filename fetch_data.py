import requests
import json
import os


class FetchData:
    @staticmethod
    def fetch_service_data(date, serviceid):
        """获取指定日期和 serviceid 的场地信息"""
        url = f"http://order.njmu.edu.cn:8088/cgyd/product/findOkArea.html"
        params = {
            "s_date": date,
            "serviceid": serviceid
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json().get('object')
            if data:
                return data
            else:
                print("没有获取到数据")
        else:
            print(f"请求失败，状态码: {response.status_code}")
        return None

    @staticmethod
    def save_data_to_json(data, date, serviceid):
        """保存获取到的数据为 JSON 文件"""
        folder = 'data'
        if not os.path.exists(folder):
            os.makedirs(folder)

        filename = os.path.join(folder, f"service_data_{serviceid}_{date}.json")
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"数据保存为 {filename}")

    @staticmethod
    def load_data_from_json(date, serviceid):
        """从指定日期的 JSON 文件加载数据"""
        folder = 'data'
        filename = os.path.join(folder, f"service_data_{serviceid}_{date}.json")
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return None
