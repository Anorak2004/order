import requests
import json
import os
from models import Venue

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


class DataImporter:
    """New class for handling JSON to database imports"""
    def __init__(self, db_session):
        self.db = db_session
        
    def import_from_json(self, json_path):
        """Import venue data from JSON file to database"""
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for item in data:
            # 添加原始ID校验
            if not item.get('id') or not item.get('stock'):
                print(f"跳过无效条目: {item.get('id')}")
                continue
                
            try:
                venue = Venue(
                    original_id=int(item['id']),  # 新增字段
                    serviceid=int(item['stock'].get('serviceid', 22)),
                    stockid=int(item['stockid']),
                    date=item['stock'].get('s_date', '').strip(),
                    time_no=item['stock'].get('time_no', '').replace(" ", ""),
                    sname=item['sname'].strip(),
                    status=1 if item.get('status') == 1 else 0
                )
                
                # 添加字段完整性检查
                if not all([venue.original_id, venue.serviceid, venue.stockid]):
                    print(f"缺失关键字段: ID={item['id']}")
                    continue
                    
                # 修改查询条件包含original_id
                exists = self.db.query(Venue).filter(
                    Venue.original_id == venue.original_id,
                    Venue.date == venue.date
                ).first()
                
                if not exists:
                    self.db.add(venue)
                    
            except (KeyError, ValueError, TypeError) as e:
                print(f"数据转换错误: {str(e)}")
                continue
                
        self.db.commit()
        print(f"Imported data from {json_path}")
