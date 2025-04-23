from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Venue(Base):
    __tablename__ = 'venues'
    
    id = Column(Integer, primary_key=True)
    original_id = Column(Integer, nullable=False, unique=True)  # 必须非空
    serviceid = Column(Integer, nullable=False)  # 添加非空约束
    stockid = Column(Integer, nullable=False)     # 添加非空约束
    date = Column(String(10), nullable=False)      # 明确长度限制
    time_no = Column(String(15), nullable=False)   # 明确长度限制
    sname = Column(String(50), nullable=False)
    status = Column(Integer)
    
class BookingRecord(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer)
    users = Column(String)
    booking_time = Column(DateTime)

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    remark = Column(String(100))
    isDefault = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联到预约任务
    auto_bookings = relationship("AutoBooking", back_populates="account")

class AutoBooking(Base):
    __tablename__ = "auto_bookings"
    
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer, nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    booking_date = Column(String(10), nullable=False)
    time_no = Column(String(15), nullable=False)
    users = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, failed, cancelled
    scheduled_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    executed_at = Column(DateTime)
    result = Column(JSON)
    
    # 关联账号
    account = relationship("Account", back_populates="auto_bookings")