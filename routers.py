from sqlalchemy.orm import Session  # 添加 Session 类型导入
from fastapi import APIRouter, Depends, HTTPException, Body
from dependencies import get_db
from repositories import VenueRepository, BookingRepository, AccountRepository, AutoBookingRepository
from typing import List, Optional
from pydantic import BaseModel, Field
import json
from datetime import datetime

router = APIRouter()

# 数据模型
class AccountCreate(BaseModel):
    username: str
    password: str
    remark: Optional[str] = None
    isDefault: Optional[bool] = False

class AccountUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    remark: Optional[str] = None
    isDefault: Optional[bool] = None

class AccountResponse(BaseModel):
    id: int
    username: str
    remark: Optional[str] = None
    isDefault: bool
    created_at: datetime

class AutoBookingCreate(BaseModel):
    venue_id: int
    account_id: int
    booking_date: str
    time_no: str
    users: str

class AutoBookingResponse(BaseModel):
    id: int
    venue_id: int
    account_id: int
    booking_date: str
    time_no: str
    users: str
    status: str
    scheduled_time: datetime
    created_at: datetime
    executed_at: Optional[datetime] = None
    result: Optional[dict] = None
    venue: Optional[dict] = None
    account: Optional[dict] = None

class PrebookWithAccount(BaseModel):
    stockid: str
    serviceid: str
    venue_id: str
    users: str
    account_id: int

# 场馆查询接口增加参数校验
# 修改所有仓库实例的获取方式
@router.get("/venues")
async def get_venues(
    serviceid: int, 
    date: str,
    db: Session = Depends(get_db)
):
    from fetch_data import FetchData, DataImporter  # 新增导入
    
    repo = VenueRepository(db)
    
    # 检查数据库是否存在该日期的数据
    if not repo.check_data_exists(serviceid, date):
        print(f"数据库无 {date} 数据，开始获取...")
        # 调用API获取数据
        api_data = FetchData.fetch_service_data(date, serviceid)
        if api_data:
            # 保存并导入数据
            FetchData.save_data_to_json(api_data, date, serviceid)
            DataImporter(db).import_from_json(
                f"data/service_data_{serviceid}_{date}.json"
            )
    
    if not serviceid or not date:
        raise HTTPException(400, "Missing required parameters")
    return repo.get_available_venues(serviceid, date)

# 预约接口增加事务处理
@router.post("/bookings")
async def create_booking(
    venue_id: int,
    users: list,
    repo: BookingRepository = Depends(lambda: BookingRepository(next(get_db())))
):
    try:
        return repo.create_booking(venue_id, users)
    except Exception as e:
        raise HTTPException(500, f"Booking failed: {str(e)}")

# 账号管理API
@router.post("/accounts", status_code=201, response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """创建新账号"""
    new_account = repo.create_account(
        username=account.username,
        password=account.password,
        remark=account.remark,
        is_default=account.isDefault
    )
    
    if not new_account:
        raise HTTPException(400, "账号已存在")
    
    return new_account

@router.get("/accounts", response_model=List[AccountResponse])
async def get_accounts(
    repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """获取所有账号"""
    return repo.get_accounts()

@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """获取特定账号"""
    account = repo.get_account_by_id(account_id)
    if not account:
        raise HTTPException(404, "账号不存在")
    return account

@router.put("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account: AccountUpdate,
    repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """更新账号信息"""
    updated = repo.update_account(
        account_id=account_id,
        password=account.password,
        remark=account.remark,
        is_default=account.isDefault
    )
    
    if not updated:
        raise HTTPException(404, "账号不存在")
    
    return updated

@router.delete("/accounts/{account_id}", status_code=204)
async def delete_account(
    account_id: int,
    repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """删除账号"""
    result = repo.delete_account(account_id)
    if not result:
        raise HTTPException(404, "账号不存在")
    return None

# 自动预约API
@router.post("/auto-bookings", status_code=201, response_model=AutoBookingResponse)
async def create_auto_booking(
    booking: AutoBookingCreate,
    repo: AutoBookingRepository = Depends(lambda: AutoBookingRepository(next(get_db()))),
    venue_repo: VenueRepository = Depends(lambda: VenueRepository(next(get_db()))),
    account_repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """创建自动预约任务"""
    # 验证场馆存在
    venue = venue_repo.get_venue_by_id(booking.venue_id)
    if not venue:
        raise HTTPException(404, "场馆不存在")
    
    # 验证账号存在
    account = account_repo.get_account_by_id(booking.account_id)
    if not account:
        raise HTTPException(404, "账号不存在")
    
    new_booking = repo.create_booking(
        venue_id=booking.venue_id,
        account_id=booking.account_id,
        booking_date=booking.booking_date,
        time_no=booking.time_no,
        users=booking.users
    )
    
    # 将关联信息添加到响应中
    response_dict = new_booking.__dict__.copy()
    
    response_dict["venue"] = {
        "id": venue.id,
        "sname": venue.sname,
        "time_no": venue.time_no
    }
    
    response_dict["account"] = {
        "id": account.id,
        "username": account.username,
        "remark": account.remark
    }
    
    return response_dict

@router.get("/auto-bookings", response_model=List[AutoBookingResponse])
async def get_auto_bookings(
    status: Optional[str] = None,
    repo: AutoBookingRepository = Depends(lambda: AutoBookingRepository(next(get_db()))),
    venue_repo: VenueRepository = Depends(lambda: VenueRepository(next(get_db()))),
    account_repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """获取自动预约任务列表"""
    bookings = repo.get_bookings(status)
    
    # 为每个任务添加关联的场馆和账号信息
    result = []
    for booking in bookings:
        booking_dict = booking.__dict__.copy()
        
        # 获取关联的场馆信息
        venue = venue_repo.get_venue_by_id(booking.venue_id)
        if venue:
            booking_dict["venue"] = {
                "id": venue.id,
                "sname": venue.sname,
                "time_no": venue.time_no
            }
        
        # 获取关联的账号信息
        account = account_repo.get_account_by_id(booking.account_id)
        if account:
            booking_dict["account"] = {
                "id": account.id,
                "username": account.username,
                "remark": account.remark
            }
        
        result.append(booking_dict)
    
    return result

@router.get("/auto-bookings/{booking_id}", response_model=AutoBookingResponse)
async def get_auto_booking(
    booking_id: int,
    repo: AutoBookingRepository = Depends(lambda: AutoBookingRepository(next(get_db()))),
    venue_repo: VenueRepository = Depends(lambda: VenueRepository(next(get_db()))),
    account_repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """获取特定自动预约任务"""
    booking = repo.get_booking_by_id(booking_id)
    if not booking:
        raise HTTPException(404, "预约任务不存在")
    
    # 获取关联的场馆和账号信息
    venue = venue_repo.get_venue_by_id(booking.venue_id)
    account = account_repo.get_account_by_id(booking.account_id)
    
    # 将关联信息添加到响应中
    response_dict = booking.__dict__.copy()
    
    if venue:
        response_dict["venue"] = {
            "id": venue.id,
            "sname": venue.sname,
            "time_no": venue.time_no
        }
    
    if account:
        response_dict["account"] = {
            "id": account.id,
            "username": account.username,
            "remark": account.remark
        }
    
    return response_dict

@router.delete("/auto-bookings/{booking_id}", status_code=204)
async def cancel_auto_booking(
    booking_id: int,
    repo: AutoBookingRepository = Depends(lambda: AutoBookingRepository(next(get_db())))
):
    """取消自动预约任务"""
    result = repo.cancel_booking(booking_id)
    if not result:
        raise HTTPException(404, "预约任务不存在或已执行")
    return None

# 使用账号ID直接预约
@router.post("/prebook-with-account")
async def prebook_with_account(
    booking: PrebookWithAccount,
    account_repo: AccountRepository = Depends(lambda: AccountRepository(next(get_db())))
):
    """使用指定账号直接预约"""
    # 获取账号信息
    account = account_repo.get_account_by_id(booking.account_id)
    if not account:
        raise HTTPException(404, "账号不存在")
    
    try:
        from book import Booking
        book = Booking(
            stockid=booking.stockid,
            serviceid=booking.serviceid,
            id=booking.venue_id,
            users=booking.users,
            username=account.username,
            password=account.password
        )
        result = book.pre_book()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(500, f"预约失败: {str(e)}")

# 在router.py末尾添加
@router.post("/import-data")
async def import_data(
    date: str,
    serviceid: int,
    repo: VenueRepository = Depends(lambda: VenueRepository(next(get_db())))
):
    """触发式数据导入接口"""
    from fetch_data import FetchData
    print(f"[Import] Starting import for serviceid={serviceid} date={date}")
    
    data = FetchData.fetch_service_data(date, serviceid)
    print(f"[Import] Received {len(data)} items from external API")
    
    venues = []
    for item in data:
        # 强化空值校验
        if not all([
            item.get('stock'),
            isinstance(item.get('id'), (int, str)),  # 允许字符串类型的ID
            isinstance(item.get('stockid'), (int, str))
        ]):
            print(f"无效条目: {item.get('id')} | stockid={item.get('stockid')}")
            continue

        try:
            # 添加类型转换保护
            from models import Venue
            venue = Venue(
                original_id=int(item['id']),
                serviceid=int(item['stock'].get('serviceid', serviceid)),
                stockid=int(str(item['stockid']).strip()),  # 处理字符串类型的stockid
                date=item['stock'].get('s_date', date).strip() or date,
                time_no=item['stock'].get('time_no', '').replace(" ", "") or '00:00-24:00',
                sname=item['sname'].strip(),
                status=1 if item.get('status') == 1 else 0
            )
            # 字段完整性校验
            if not all([venue.original_id, venue.serviceid, venue.stockid, venue.date, venue.time_no]):
                print(f"无效数据条目: ID={item['id']}, 缺失关键字段")
                continue
            venues.append(venue)
        except (KeyError, ValueError, TypeError) as e:
            print(f"数据转换错误: {str(e)}, 原始数据: {item}")
            continue

    # 添加空数据集校验
    if not venues:
        raise HTTPException(400, "导入数据全部无效，请检查原始数据格式")
    
    # 添加空值检查
    if any(not v.original_id for v in venues):
        raise HTTPException(400, "发现无效的原始ID")
    if venues:
        sample = venues[0]
        print(f"[Import] 字段验证: id={sample.original_id} | date={sample.date} | time_no={sample.time_no}")
    # 添加字段类型验证
    if venues:
        invalid_dates = [v for v in venues if not isinstance(v.date, str) or len(v.date) != 10]
        if invalid_dates:
            print(f"[ERROR] 发现 {len(invalid_dates)} 条无效日期格式")
    # 添加详细字段跟踪
    if data:
        print(f"[DEBUG] 原始数据第一条的stock字段: {json.dumps(data[0]['stock'], ensure_ascii=False)}")
    # 添加详细字段验证
    if venues:
        stock_sample = data[0]['stock']
        print(f"[Import] 字段源数据验证: serviceid={stock_sample.get('serviceid')} | date={stock_sample.get('s_date')} | time_no={stock_sample.get('time_no')}")
    # 添加字段验证日志
    if venues:
        sample = venues[0]
        print(f"[Import] 字段验证: date={sample.date} | time_no={sample.time_no} | stockid={sample.stockid}")
    print(f"[Import] First venue sample: {venues[0].__dict__ if venues else 'No data'}")
    
    repo.bulk_create(venues)
    return {"imported": len(venues)}


@router.get("/debug/connection")
async def test_db_connection(db: Session = Depends(get_db)):
    """测试数据库连接"""
    try:
        result = db.execute("SELECT 1")
        return {"status": "connected", "result": result.scalar()}
    except Exception as e:
        return {"error": str(e)}

@router.get("/debug/venues")
async def debug_venues(
    serviceid: int,
    date: str,
    db: Session = Depends(get_db)
):
    """原始SQL查询调试接口"""
    result = db.execute(f"""
        SELECT * FROM venues 
        WHERE serviceid = {serviceid} 
        AND date = '{date}'
        AND status = 1
    """)
    return [dict(row) for row in result]

# 在现有路由后添加新的预约接口
@router.post("/prebook")
async def prebook_venue(
    stockid: str,
    serviceid: str,
    venue_id: str,
    users: str,
    username: str,
    password: str
):
    """直接预约接口（模拟new_order.py逻辑）"""
    try:
        from book import Booking
        book = Booking(
            stockid=stockid,
            serviceid=serviceid,
            id=venue_id,
            users=users,
            username=username,
            password=password
        )
        result = book.pre_book()
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(500, f"预约失败: {str(e)}")