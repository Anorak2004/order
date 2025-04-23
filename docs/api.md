# API参考

本文档详细说明系统提供的API接口、参数和返回值。

## API概述

系统使用FastAPI框架提供RESTful API服务，API根路径为`/api/v1`。所有API都遵循RESTful设计原则，使用JSON格式进行数据交换。

API文档可通过访问`/api/docs`或`/api/redoc`获取自动生成的交互式文档。

## 认证与授权

当前API不需要认证即可访问，但预约接口会使用配置中的登录信息进行认证。

## API端点

### 场馆查询接口

获取指定日期和类型的可用场馆信息。

**请求**:
- 方法: `GET`
- 路径: `/api/v1/venues`
- 参数:
  - `serviceid` (整数，必填): 场馆类型ID
  - `date` (字符串，必填): 查询日期，格式为 YYYY-MM-DD

**响应**:
- 状态码: 200 OK
- 内容类型: application/json
- 响应体: 场馆对象数组

```json
[
  {
    "id": 1,
    "original_id": 144995,
    "serviceid": 22,
    "stockid": 10382,
    "date": "2024-04-01",
    "time_no": "20:01-21:00",
    "sname": "篮球场2号",
    "status": 1
  },
  ...
]
```

**错误响应**:
- 400 Bad Request: 缺少必要参数
- 500 Internal Server Error: 服务器内部错误

**示例请求**:
```
GET /api/v1/venues?serviceid=22&date=2024-04-01
```

### 预约创建接口

创建新的场馆预约记录。

**请求**:
- 方法: `POST`
- 路径: `/api/v1/bookings`
- 参数:
  - `venue_id` (整数，必填): 场馆ID
  - `users` (数组，必填): 预约用户ID列表

**响应**:
- 状态码: 200 OK
- 内容类型: application/json
- 响应体: 创建的预约记录对象

```json
{
  "id": 1,
  "venue_id": 1,
  "users": "160734,160747",
  "booking_time": "2024-04-01T10:30:00"
}
```

**错误响应**:
- 400 Bad Request: 缺少必要参数
- 500 Internal Server Error: 预约失败

**示例请求**:
```
POST /api/v1/bookings
Content-Type: application/json

{
  "venue_id": 1,
  "users": ["160734", "160747"]
}
```

### 直接预约接口

直接调用外部系统API进行预约。

**请求**:
- 方法: `POST`
- 路径: `/api/v1/prebook`
- 参数:
  - `stockid` (字符串，必填): 库存ID
  - `serviceid` (字符串，必填): 场馆类型ID
  - `venue_id` (字符串，必填): 场馆ID
  - `users` (字符串，必填): 用户ID，多个用逗号分隔
  - `username` (字符串，必填): 登录用户名
  - `password` (字符串，必填): 登录密码

**响应**:
- 状态码: 200 OK
- 内容类型: application/json
- 响应体: 预约结果对象

```json
{
  "status": "success",
  "result": {
    "result": "1",
    "message": "预订成功"
  }
}
```

**错误响应**:
- 400 Bad Request: 缺少必要参数
- 500 Internal Server Error: 预约失败

**示例请求**:
```
POST /api/v1/prebook
Content-Type: application/json

{
  "stockid": "10382",
  "serviceid": "22",
  "venue_id": "144995",
  "users": "160734,160747",
  "username": "22011207",
  "password": "password"
}
```

### 数据导入接口

触发式导入指定日期和类型的场馆数据。

**请求**:
- 方法: `POST`
- 路径: `/api/v1/import-data`
- 参数:
  - `date` (字符串，必填): 日期，格式为 YYYY-MM-DD
  - `serviceid` (整数，必填): 场馆类型ID

**响应**:
- 状态码: 200 OK
- 内容类型: application/json
- 响应体: 导入结果对象

```json
{
  "imported": 10
}
```

**错误响应**:
- 400 Bad Request: 数据格式无效
- 500 Internal Server Error: 导入失败

**示例请求**:
```
POST /api/v1/import-data
Content-Type: application/json

{
  "date": "2024-04-01",
  "serviceid": 22
}
```

### 数据库连接测试

测试数据库连接是否正常。

**请求**:
- 方法: `GET`
- 路径: `/api/v1/debug/connection`

**响应**:
- 状态码: 200 OK
- 内容类型: application/json
- 响应体: 连接测试结果

```json
{
  "status": "connected",
  "result": 1
}
```

**错误响应**:
- 500 Internal Server Error: 连接失败

**示例请求**:
```
GET /api/v1/debug/connection
```

### 场馆原始查询

使用原始SQL查询场馆数据（调试用）。

**请求**:
- 方法: `GET`
- 路径: `/api/v1/debug/venues`
- 参数:
  - `serviceid` (整数，必填): 场馆类型ID
  - `date` (字符串，必填): 查询日期，格式为 YYYY-MM-DD

**响应**:
- 状态码: 200 OK
- 内容类型: application/json
- 响应体: 场馆对象数组

```json
[
  {
    "id": 1,
    "original_id": 144995,
    "serviceid": 22,
    "stockid": 10382,
    "date": "2024-04-01",
    "time_no": "20:01-21:00",
    "sname": "篮球场2号",
    "status": 1
  },
  ...
]
```

**错误响应**:
- 400 Bad Request: 缺少必要参数
- 500 Internal Server Error: 查询错误

**示例请求**:
```
GET /api/v1/debug/venues?serviceid=22&date=2024-04-01
```

## 数据模型

### Venue (场馆)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | 整数 | 主键 |
| original_id | 整数 | 原系统ID |
| serviceid | 整数 | 场馆类型ID |
| stockid | 整数 | 库存ID |
| date | 字符串 | 日期 (YYYY-MM-DD) |
| time_no | 字符串 | 时间段 (HH:MM-HH:MM) |
| sname | 字符串 | 场馆名称 |
| status | 整数 | 状态 (1=可用, 0=不可用) |

### BookingRecord (预约记录)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | 整数 | 主键 |
| venue_id | 整数 | 场馆ID |
| users | 字符串 | 用户ID，多个用逗号分隔 |
| booking_time | 日期时间 | 预约时间 |

## 状态码

API使用标准HTTP状态码：

- **200 OK**: 请求成功
- **400 Bad Request**: 请求参数无效
- **404 Not Found**: 资源不存在
- **500 Internal Server Error**: 服务器内部错误

## 错误处理

所有错误响应遵循统一格式：

```json
{
  "detail": "错误信息描述"
}
```

## 使用示例

### cURL示例

查询场馆：
```bash
curl -X GET "http://localhost:8000/api/v1/venues?serviceid=22&date=2024-04-01"
```

创建预约：
```bash
curl -X POST "http://localhost:8000/api/v1/bookings" \
  -H "Content-Type: application/json" \
  -d '{"venue_id": 1, "users": ["160734", "160747"]}'
```

### Python示例

```python
import requests

# 查询场馆
response = requests.get(
    "http://localhost:8000/api/v1/venues",
    params={"serviceid": 22, "date": "2024-04-01"}
)
venues = response.json()
print(f"找到 {len(venues)} 个可用场馆")

# 创建预约
if venues:
    venue_id = venues[0]["id"]
    response = requests.post(
        "http://localhost:8000/api/v1/bookings",
        json={"venue_id": venue_id, "users": ["160734", "160747"]}
    )
    print(f"预约结果: {response.json()}")
```

## 注意事项

1. 所有日期格式必须为 YYYY-MM-DD
2. 预约接口会使用配置中的登录信息，确保其正确性
3. 导入接口可能需要较长时间处理，建议设置合理的超时时间
4. 预约操作是幂等的，重复预约同一场馆会返回错误 