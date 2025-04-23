from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Index  # 添加 Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
import threading
from contextlib import asynccontextmanager
from routers import router as api_router
from models import Base, Venue, BookingRecord, Account, AutoBooking  # 修改导入来源
from dependencies import get_db  # 新增导入

# 数据库初始化
engine = create_engine('sqlite:///./data/reservation.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据模型
# 数据库初始化
# Remove the duplicate Base declaration and keep this line:
from models import Base, Venue, BookingRecord, Account, AutoBooking

# 创建数据库表
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行的代码
    from pathlib import Path
    from fetch_data import DataImporter
    
    print("正在扫描数据文件...")  # 添加初始化日志
    json_files = list(Path("data").glob("service_data_*.json"))
    print(f"找到 {len(json_files)} 个数据文件")
    
    importer = DataImporter(SessionLocal())
    for file in json_files:
        print(f"正在导入文件: {file.name}")
        importer.import_from_json(file)
    
    # 启动自动预约执行器（异步启动，不阻塞主程序）
    def start_auto_booker():
        from auto_booker import AutoBooker
        AutoBooker.start_scheduler()
    
    # 创建并启动线程
    auto_booker_thread = threading.Thread(target=start_auto_booker, daemon=True)
    auto_booker_thread.start()
    print("自动预约执行器已启动")
    
    yield  # 应用运行
    # 关闭时执行的代码
    print("应用正在关闭...")

app = FastAPI(
    title="场馆预约系统",
    description="南京医科大学场馆预约API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)
app.include_router(api_router, prefix="/api/v1")  # 添加路由挂载

# Create static directory if not exists
static_dir = "static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# 依赖注入
# 删除原有的 get_db 函数定义
