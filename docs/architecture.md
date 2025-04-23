# 系统架构

本文档详细描述系统的架构设计、技术栈和核心组件。

## 架构概览

南京医科大学场馆预约系统采用经典的分层架构，将系统划分为数据层、业务逻辑层和接口层。整体架构如下图所示：

```
+------------------+
|      接口层      |     FastAPI, CLI
+------------------+
|    业务逻辑层    |     Service模块, 工具类
+------------------+
|      数据层      |     Repository, SQLAlchemy ORM
+------------------+
|     数据存储     |     SQLite数据库, JSON文件
+------------------+
```

## 技术栈详情

### 后端技术栈

- **Web框架**: FastAPI - 高性能的Python异步Web框架
- **数据库**: SQLite - 轻量级文件数据库系统
- **ORM**: SQLAlchemy - Python中最流行的ORM库
- **HTTP客户端**: Requests - 简单易用的HTTP库
- **定时任务**: Schedule - 轻量级Python调度库
- **命令行**: 基于Python内置库的交互式CLI

### 设计模式

系统应用了多种设计模式：

1. **仓储模式(Repository Pattern)**: 用于分离数据访问逻辑与业务逻辑
2. **依赖注入(Dependency Injection)**: 在FastAPI中广泛使用，提高代码可测试性
3. **单例模式(Singleton)**: 用于数据库连接管理
4. **策略模式(Strategy)**: 用于不同场馆类型的数据获取策略
5. **命令模式(Command)**: 用于CLI命令的实现

## 模块组织

系统按照功能模块进行组织，主要模块包括：

### 核心模块

- **models.py**: 数据模型定义
- **repositories.py**: 数据访问层封装
- **fetch_data.py**: 数据获取与同步
- **book.py**: 预约核心逻辑
- **login.py**: 用户认证逻辑

### 接口模块

- **main.py**: 应用程序入口，FastAPI初始化
- **routers.py**: API路由定义
- **cli.py**: 命令行界面

### 配置和工具模块

- **config.py**: 系统配置
- **config_setup.py**: 配置初始化工具
- **utils.py**: 通用工具函数
- **scheduler.py**: 定时任务实现
- **dependencies.py**: 依赖注入配置

## 核心组件详解

### FastAPI应用

FastAPI应用是系统的主要接口，提供RESTful API服务。主要特点包括：

- 自动生成API文档 (OpenAPI/Swagger)
- 请求参数验证和类型提示
- 基于依赖注入的数据库会话管理
- 异步请求处理支持

### 数据访问层

采用仓储模式(Repository Pattern)封装数据访问逻辑：

```python
class VenueRepository:
    def __init__(self, db: Session):
        self.db = db
        
    def get_available_venues(self, serviceid: int, date: str):
        return self.db.query(Venue).filter(
            Venue.serviceid == serviceid,
            Venue.date == date,
            Venue.status == 1
        ).all()
```

这种设计使业务逻辑不直接依赖于数据库操作，提高了代码的可测试性和可维护性。

### 数据模型

系统使用SQLAlchemy定义数据模型，主要包括：

- **Venue**: 场馆信息模型
- **BookingRecord**: 预约记录模型

模型定义示例：

```python
class Venue(Base):
    __tablename__ = 'venues'
    
    id = Column(Integer, primary_key=True)
    original_id = Column(Integer, nullable=False, unique=True)
    serviceid = Column(Integer, nullable=False)
    stockid = Column(Integer, nullable=False)
    date = Column(String(10), nullable=False)
    time_no = Column(String(15), nullable=False)
    sname = Column(String(50), nullable=False)
    status = Column(Integer)
```

### 数据同步

系统使用`FetchData`类实现从原系统API获取场馆数据：

1. 根据日期和场馆类型请求API获取数据
2. 将数据保存为JSON文件
3. 使用`DataImporter`将数据导入本地数据库

### 预约逻辑

预约逻辑是系统的核心，主要步骤包括：

1. 用户登录获取会话
2. 构建预约请求参数
3. 发送预约请求
4. 处理响应结果，失败时自动重试

### 命令行界面

系统提供了交互式命令行界面，主要功能包括：

1. 提示用户输入日期和场馆类型
2. 展示可用场馆列表
3. 接收用户选择并配置预约参数
4. 执行预约操作

### 定时任务

系统使用Schedule库实现定时预约任务：

1. 配置预约参数
2. 设置每天执行时间
3. 在指定时间自动执行预约

## 数据流

### 场馆数据流

```
外部API -> JSON文件 -> 本地数据库 -> API/CLI查询结果
```

### 预约流程

```
用户输入 -> 构建请求 -> 发送到外部API -> 处理响应 -> 返回结果
```

## 扩展性考虑

系统设计时考虑了扩展性：

1. **模块化设计**: 功能封装在独立模块中，便于替换或增强
2. **数据访问抽象**: 通过Repository模式隔离数据访问细节
3. **配置外部化**: 关键参数可通过配置文件调整
4. **接口分离**: API与CLI分离，便于添加其他接口类型

## 性能优化

系统在以下方面进行了性能优化：

1. **数据缓存**: 本地数据库缓存场馆数据，减少API请求
2. **批量操作**: 使用批量导入减少数据库操作次数
3. **数据库索引**: 关键查询字段添加了索引
4. **懒加载**: 部分模块采用延迟导入，减少启动时间

## 安全考虑

系统在以下方面考虑了安全性：

1. **参数验证**: API接口参数进行类型检查和验证
2. **SQL注入防护**: 使用ORM避免SQL注入风险
3. **错误处理**: 全局异常处理，避免敏感信息泄露

## 依赖管理

系统使用requirements.txt管理依赖，主要依赖包括：

- requests: HTTP客户端
- fastapi: Web框架
- sqlalchemy: ORM库
- uvicorn: ASGI服务器
- schedule: 定时任务库 