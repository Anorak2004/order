# 模块说明

本文档详细介绍系统的主要模块、类和函数，以及它们之间的关系。

## 核心模块

### models.py

该模块定义了系统的数据模型，使用SQLAlchemy ORM框架。

#### Venue

场馆信息模型，存储从外部系统获取的场馆数据。

```python
class Venue(Base):
    __tablename__ = 'venues'
    
    id = Column(Integer, primary_key=True)
    original_id = Column(Integer, nullable=False, unique=True)  # 原系统ID
    serviceid = Column(Integer, nullable=False)  # 场馆类型ID
    stockid = Column(Integer, nullable=False)  # 库存ID
    date = Column(String(10), nullable=False)  # 日期
    time_no = Column(String(15), nullable=False)  # 时间段
    sname = Column(String(50), nullable=False)  # 场馆名称
    status = Column(Integer)  # 状态，1表示可用
```

#### BookingRecord

预约记录模型，存储用户预约信息。

```python
class BookingRecord(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True)
    venue_id = Column(Integer)  # 场馆ID
    users = Column(String)  # 预约用户
    booking_time = Column(DateTime)  # 预约时间
```

### repositories.py

该模块实现数据访问层，封装数据库操作逻辑。

#### VenueRepository

场馆数据仓库，提供场馆数据的查询和管理方法。

主要方法：
- `get_available_venues(serviceid, date)`: 获取指定日期和类型的可用场馆
- `bulk_create(venues)`: 批量创建场馆记录
- `check_data_exists(serviceid, date)`: 检查指定日期的数据是否存在

#### BookingRepository

预约记录仓库，提供预约记录的创建和查询方法。

主要方法：
- `create_booking(venue_id, users)`: 创建预约记录

### fetch_data.py

该模块负责从外部API获取场馆数据并保存到本地。

#### FetchData

提供场馆数据获取和管理方法的静态类。

主要方法：
- `fetch_service_data(date, serviceid)`: 从外部API获取场馆数据
- `save_data_to_json(data, date, serviceid)`: 将数据保存为JSON文件
- `load_data_from_json(date, serviceid)`: 从JSON文件加载数据

#### DataImporter

负责将JSON数据导入到数据库的类。

主要方法：
- `import_from_json(json_path)`: 从JSON文件导入数据到数据库

### book.py

该模块实现预约功能的核心逻辑。

#### Booking

预约功能实现类，处理场馆预约请求。

主要方法：
- `__init__(stockid, serviceid, id, users, username, password)`: 初始化预约参数
- `pre_book()`: 发送预约请求
- `book_venue()`: 静态方法，使用配置信息进行预约

### login.py

该模块处理用户登录和认证。

#### Login

用户登录类，处理登录请求和会话管理。

主要方法：
- `__init__(username, password)`: 初始化登录参数
- `pre_login()`: 发送登录请求并获取会话

## 接口模块

### main.py

系统入口模块，配置和启动FastAPI应用。

主要组件：
- FastAPI应用初始化
- 数据库连接配置
- 路由挂载
- 启动事件处理（数据初始化）

### routers.py

API路由定义模块，实现系统的REST API接口。

主要接口：
- `GET /venues`: 场馆查询接口
- `POST /bookings`: 预约创建接口
- `POST /import-data`: 数据导入接口
- `POST /prebook`: 直接预约接口
- `GET /debug/connection`: 数据库连接测试
- `GET /debug/venues`: 场馆原始查询

### cli.py

命令行界面模块，提供交互式命令行操作。

主要函数：
- `prompt_for_date_and_serviceid()`: 提示用户输入日期和场馆类型
- `display_options(data)`: 展示场馆选项
- `get_user_choice(prompt, total_options)`: 获取用户选择
- `run_cli()`: CLI主函数

## 配置和工具模块

### config.py

系统配置模块，定义系统配置参数。

主要配置：
- `LOGIN_DATA`: 登录信息配置
- `BOOKING_DATA`: 预约参数配置
- `BASE_URL`: 外部系统基础URL
- `BOOKING_HOURS`: 预约时间规则
- `SCHEDULE_TIME`: 定时任务执行时间

#### Config类方法
- `is_booking_time()`: 判断当前是否在允许预约的时间段

### config_setup.py

配置初始化工具，用于交互式设置系统配置。

主要函数：
- `setup_config()`: 设置预约参数

### scheduler.py

定时任务实现模块，用于自动预约。

主要函数：
- `check_booking_conditions()`: 检查预约条件并执行预约
- `start_scheduler()`: 启动定时任务

### dependencies.py

依赖注入配置模块，定义FastAPI依赖项。

主要依赖：
- `get_db()`: 数据库会话依赖

### utils.py

通用工具函数模块，提供辅助功能。

主要函数：
- 工具函数和辅助函数

## 模块间关系

### 数据流向

1. **数据获取流程**:
   ```
   fetch_data.py (FetchData) -> JSON文件 -> fetch_data.py (DataImporter) -> models.py -> SQLite数据库
   ```

2. **查询流程**:
   ```
   routers.py/cli.py -> repositories.py -> models.py -> SQLite数据库
   ```

3. **预约流程**:
   ```
   routers.py/cli.py -> book.py -> 外部API -> 处理响应
   ```

### 依赖关系

- **main.py**: 依赖 models.py, routers.py, dependencies.py, fetch_data.py
- **routers.py**: 依赖 dependencies.py, repositories.py, fetch_data.py, book.py
- **repositories.py**: 依赖 models.py
- **book.py**: 依赖 config.py, login.py
- **fetch_data.py**: 依赖 models.py
- **cli.py**: 依赖 fetch_data.py, config.py, book.py
- **scheduler.py**: 依赖 book.py, config.py, config_setup.py

## 文件目录结构

```
/
├── main.py              # 应用入口
├── models.py            # 数据模型
├── repositories.py      # 数据访问层
├── routers.py           # API路由
├── dependencies.py      # 依赖注入
├── fetch_data.py        # 数据获取
├── book.py              # 预约逻辑
├── login.py             # 登录认证
├── config.py            # 系统配置
├── config_setup.py      # 配置初始化
├── scheduler.py         # 定时任务
├── cli.py               # 命令行界面
├── utils.py             # 工具函数
├── requirements.txt     # 依赖列表
├── data/                # 数据目录
│   └── reservation.db   # 数据库文件
└── static/              # 静态文件目录
```

## 扩展和定制

### 添加新场馆类型

1. 确定新场馆类型的`serviceid`
2. 无需修改数据模型，现有模型可适配
3. 在`config.py`中添加新场馆类型的配置

### 修改预约逻辑

1. 更新`book.py`中的`Booking`类
2. 修改预约请求的构建和发送逻辑

### 添加新的API接口

1. 在`routers.py`中添加新的路由函数
2. 如需新的数据访问逻辑，扩展`repositories.py`中的相关仓库类

### 修改数据模型

1. 在`models.py`中更新模型定义
2. 注意处理数据库迁移，可能需要编写迁移脚本

## 最佳实践

### 代码组织

- 保持单一职责原则，每个模块专注于特定功能
- 使用仓储模式隔离数据访问逻辑
- 通过依赖注入提高代码可测试性

### 配置管理

- 敏感信息（如登录凭证）应移至环境变量或安全存储
- 使用配置文件或环境变量控制系统行为
- 避免在代码中硬编码配置参数

### 错误处理

- 使用异常处理捕获和处理错误
- 记录错误信息到日志
- 返回用户友好的错误信息 