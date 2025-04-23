"""
自动预约执行器
检查和执行到期的预约任务
"""
import time
import schedule
from datetime import datetime, timedelta
import threading
from sqlalchemy.orm import Session
from repositories import AutoBookingRepository
from book import Booking
from main import SessionLocal
from models import Account, Venue

class AutoBooker:
    """自动预约执行器"""
    
    @staticmethod
    def check_and_execute_bookings():
        """检查并执行到期的预约任务"""
        print(f"[AutoBooker] 开始检查预约任务，当前时间: {datetime.now()}")
        
        db = SessionLocal()
        try:
            repo = AutoBookingRepository(db)
            bookings = repo.get_bookings_to_execute()
            
            print(f"[AutoBooker] 找到 {len(bookings)} 个需要执行的预约任务")
            
            for booking in bookings:
                try:
                    print(f"[AutoBooker] 执行预约任务 ID: {booking.id}")
                    
                    # 查询账号信息
                    account = db.query(Account).filter(Account.id == booking.account_id).first()
                    
                    if not account:
                        print(f"[AutoBooker] 账号不存在: {booking.account_id}")
                        repo.update_booking_status(
                            booking_id=booking.id, 
                            status="failed", 
                            result={"error": "账号不存在"}
                        )
                        continue
                    
                    # 查询场馆信息
                    venue = db.query(Venue).filter(Venue.id == booking.venue_id).first()
                    
                    if not venue:
                        print(f"[AutoBooker] 场馆不存在: {booking.venue_id}")
                        repo.update_booking_status(
                            booking_id=booking.id, 
                            status="failed", 
                            result={"error": "场馆不存在"}
                        )
                        continue
                    
                    # 执行预约
                    book = Booking(
                        stockid=str(venue.stockid),
                        serviceid=str(venue.serviceid),
                        id=str(venue.original_id),
                        users=booking.users,
                        username=account.username,
                        password=account.password
                    )
                    
                    result = book.pre_book()
                    
                    # 更新任务状态
                    repo.update_booking_status(
                        booking_id=booking.id,
                        status="completed",
                        result=result
                    )
                    
                    print(f"[AutoBooker] 预约成功: {booking.id}")
                    
                except Exception as e:
                    print(f"[AutoBooker] 预约失败: {booking.id}, 错误: {str(e)}")
                    repo.update_booking_status(
                        booking_id=booking.id,
                        status="failed",
                        result={"error": str(e)}
                    )
        
        finally:
            db.close()
    
    @staticmethod
    def schedule_precise_tasks():
        """根据数据库中的任务，安排精确的执行计划"""
        db = SessionLocal()
        try:
            repo = AutoBookingRepository(db)
            # 获取所有待执行的任务
            pending_tasks = repo.get_all_pending_bookings()
            
            # 清除所有当前计划
            schedule.clear()
            
            # 为每个任务安排精确的执行时间
            for task in pending_tasks:
                # 如果执行时间在未来5分钟以内，使用线程安排精确执行
                now = datetime.now()
                time_diff = (task.scheduled_time - now).total_seconds()
                
                if 0 <= time_diff <= 300:  # 5分钟内
                    print(f"[AutoBooker] 为任务 {task.id} 安排精确执行计划，将在 {task.scheduled_time} 执行")
                    # 使用线程安排精确执行
                    t = threading.Timer(time_diff, AutoBooker.execute_specific_task, args=[task.id])
                    t.daemon = True
                    t.start()
                elif time_diff > 0:
                    # 仍然保留每小时检查一次的调度
                    pass
            
            # 每小时检查一次，更新执行计划
            schedule.every(1).hours.do(AutoBooker.schedule_precise_tasks)
            
            # 每分钟仍然检查一次，作为备份机制
            schedule.every(1).minutes.do(AutoBooker.check_and_execute_bookings)
            
        finally:
            db.close()
    
    @staticmethod
    def execute_specific_task(task_id: int):
        """执行特定的预约任务"""
        print(f"[AutoBooker] 开始执行特定预约任务 ID: {task_id}, 当前时间: {datetime.now()}")
        
        db = SessionLocal()
        try:
            repo = AutoBookingRepository(db)
            # 获取指定任务
            booking = repo.get_booking_by_id(task_id)
            
            if not booking or booking.status != "pending":
                print(f"[AutoBooker] 任务不存在或不处于待执行状态: {task_id}")
                return
                
            # 查询账号信息
            account = db.query(Account).filter(Account.id == booking.account_id).first()
            
            if not account:
                print(f"[AutoBooker] 账号不存在: {booking.account_id}")
                repo.update_booking_status(
                    booking_id=booking.id, 
                    status="failed", 
                    result={"error": "账号不存在"}
                )
                return
            
            # 查询场馆信息
            venue = db.query(Venue).filter(Venue.id == booking.venue_id).first()
            
            if not venue:
                print(f"[AutoBooker] 场馆不存在: {booking.venue_id}")
                repo.update_booking_status(
                    booking_id=booking.id, 
                    status="failed", 
                    result={"error": "场馆不存在"}
                )
                return
            
            # 执行预约
            book = Booking(
                stockid=str(venue.stockid),
                serviceid=str(venue.serviceid),
                id=str(venue.original_id),
                users=booking.users,
                username=account.username,
                password=account.password
            )
            
            result = book.pre_book()
            
            # 更新任务状态
            repo.update_booking_status(
                booking_id=booking.id,
                status="completed",
                result=result
            )
            
            print(f"[AutoBooker] 预约成功: {booking.id}")
            
        except Exception as e:
            print(f"[AutoBooker] 预约失败: {task_id}, 错误: {str(e)}")
            repo.update_booking_status(
                booking_id=task_id,
                status="failed",
                result={"error": str(e)}
            )
        finally:
            db.close()
            
    @staticmethod
    def start_scheduler():
        """启动定时任务"""
        # 首先安排精确任务
        AutoBooker.schedule_precise_tasks()
        
        print("[AutoBooker] 自动预约执行器已启动")
        
        while True:
            schedule.run_pending()
            time.sleep(1)  # 每秒检查一次任务队列，提高响应速度

if __name__ == "__main__":
    # 立即安排精确任务
    AutoBooker.schedule_precise_tasks()
    
    # 启动定时任务
    AutoBooker.start_scheduler() 