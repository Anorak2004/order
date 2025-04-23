from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from models import Venue, BookingRecord, Account, AutoBooking  # 修改导入来源

class VenueRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_available_venues(self, serviceid: int, date: str):
        print(f"查询参数 serviceid={serviceid}, date={date}")  # 添加参数日志
        query = self.db.query(Venue).filter(
            Venue.serviceid == serviceid,
            Venue.date == date,
            Venue.status == 1
        )
        print(f"生成SQL: {str(query)}")  # 输出实际执行的SQL
        return query.all()

    # 新增批量创建方法
    def bulk_create(self, venues: list):
        self.db.bulk_save_objects(venues)
        self.db.commit()

    def check_data_exists(self, serviceid: int, date: str) -> bool:
        """检查指定日期的数据是否存在"""
        return self.db.query(Venue).filter(
            Venue.serviceid == serviceid,
            Venue.date == date
        ).count() > 0
        
    def get_venue_by_id(self, venue_id: int):
        """通过ID获取场馆"""
        return self.db.query(Venue).filter(Venue.id == venue_id).first()

class BookingRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create_booking(self, venue_id: int, users: list):
        record = BookingRecord(
            venue_id=venue_id,
            users=",".join(users),
            booking_time=datetime.now()
        )
        self.db.add(record)
        self.db.commit()
        return record
        
class AccountRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create_account(self, username: str, password: str, remark: str = None, is_default: bool = False):
        """创建新账号"""
        # 检查用户名是否已存在
        existing = self.db.query(Account).filter(Account.username == username).first()
        if existing:
            return None
            
        # 如果设为默认账号，需要将其他账号的默认标记设为False
        if is_default:
            self.db.query(Account).filter(Account.isDefault == True).update({Account.isDefault: False})
            
        account = Account(
            username=username,
            password=password,
            remark=remark,
            isDefault=is_default
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
        
    def get_accounts(self):
        """获取所有账号"""
        return self.db.query(Account).all()
        
    def get_account_by_id(self, account_id: int):
        """通过ID获取账号"""
        return self.db.query(Account).filter(Account.id == account_id).first()
        
    def update_account(self, account_id: int, password: str = None, remark: str = None, is_default: bool = None):
        """更新账号信息"""
        account = self.get_account_by_id(account_id)
        if not account:
            return None
            
        # 如果设为默认账号，需要将其他账号的默认标记设为False
        if is_default:
            self.db.query(Account).filter(Account.isDefault == True).update({Account.isDefault: False})
            
        if password:
            account.password = password
        if remark is not None:
            account.remark = remark
        if is_default is not None:
            account.isDefault = is_default
            
        self.db.commit()
        self.db.refresh(account)
        return account
        
    def delete_account(self, account_id: int):
        """删除账号"""
        account = self.get_account_by_id(account_id)
        if not account:
            return False
            
        self.db.delete(account)
        self.db.commit()
        return True
        
    def get_default_account(self):
        """获取默认账号"""
        return self.db.query(Account).filter(Account.isDefault == True).first()
        
class AutoBookingRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def create_booking(self, venue_id: int, account_id: int, booking_date: str, time_no: str, users: str):
        """创建自动预约任务"""
        # 计算预约执行时间（前一天的8:00:05）
        booking_date_obj = datetime.strptime(booking_date, "%Y-%m-%d")
        scheduled_day = booking_date_obj - timedelta(days=1)
        scheduled_time = datetime(
            scheduled_day.year, 
            scheduled_day.month, 
            scheduled_day.day, 
            8, 0, 5
        )
        
        booking = AutoBooking(
            venue_id=venue_id,
            account_id=account_id,
            booking_date=booking_date,
            time_no=time_no,
            users=users,
            scheduled_time=scheduled_time,
            status="pending"
        )
        
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
        
    def get_bookings(self, status: str = None):
        """获取预约任务列表"""
        query = self.db.query(AutoBooking)
        if status:
            query = query.filter(AutoBooking.status == status)
        return query.all()
        
    def get_booking_by_id(self, booking_id: int):
        """通过ID获取预约任务"""
        return self.db.query(AutoBooking).filter(AutoBooking.id == booking_id).first()
        
    def get_bookings_to_execute(self):
        """获取需要执行的预约任务（时间到了且状态为pending）"""
        now = datetime.now()
        return self.db.query(AutoBooking).filter(
            AutoBooking.status == "pending",
            AutoBooking.scheduled_time <= now
        ).all()
        
    def get_all_pending_bookings(self):
        """获取所有待执行的任务，不考虑执行时间"""
        return self.db.query(AutoBooking).filter(
            AutoBooking.status == "pending"
        ).all()
        
    def update_booking_status(self, booking_id: int, status: str, result=None):
        """更新预约任务状态"""
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            return None
            
        booking.status = status
        if status in ["completed", "failed"]:
            booking.executed_at = datetime.now()
            booking.result = result
            
        self.db.commit()
        self.db.refresh(booking)
        return booking
        
    def cancel_booking(self, booking_id: int):
        """取消预约任务"""
        booking = self.get_booking_by_id(booking_id)
        if not booking or booking.status != "pending":
            return False
            
        booking.status = "cancelled"
        self.db.commit()
        return True
        
    def delete_booking(self, booking_id: int):
        """删除预约任务"""
        booking = self.get_booking_by_id(booking_id)
        if not booking:
            return False
            
        self.db.delete(booking)
        self.db.commit()
        return True