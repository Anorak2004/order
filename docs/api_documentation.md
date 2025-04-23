# 场馆预约系统API文档

## 基础信息
- 基础URL: `http://localhost:8000/api/v1`
- 所有POST请求需设置请求头 `Content-Type: application/json`
- 所有请求体必须是JSON格式

## 1. 账号管理

### 1.1 创建账号
- **URL**: `/accounts`
- **方法**: `POST`
- **描述**: 创建新的账号
- **请求体**:
```json
{
  "username": "用户名",
  "password": "密码",
  "remark": "备注信息（可选）",
  "isDefault": false  // 是否设为默认账号（可选）
}
```
- **响应**: 201 Created
```json
{
  "id": 1,
  "username": "用户名",
  "remark": "备注信息",
  "isDefault": false,
  "created_at": "2024-04-25T10:30:00"
}
```

### 1.2 获取所有账号
- **URL**: `/accounts`
- **方法**: `GET`
- **描述**: 获取所有账号列表
- **响应**: 200 OK
```json
[
  {
    "id": 1,
    "username": "用户名1",
    "remark": "备注1",
    "isDefault": true,
    "created_at": "2024-04-25T10:30:00"
  },
  {
    "id": 2,
    "username": "用户名2",
    "remark": "备注2",
    "isDefault": false,
    "created_at": "2024-04-25T11:20:00"
  }
]
```

### 1.3 获取单个账号
- **URL**: `/accounts/{account_id}`
- **方法**: `GET`
- **描述**: 获取特定账号信息
- **响应**: 200 OK
```json
{
  "id": 1,
  "username": "用户名",
  "remark": "备注信息",
  "isDefault": false,
  "created_at": "2024-04-25T10:30:00"
}
```

### 1.4 更新账号
- **URL**: `/accounts/{account_id}`
- **方法**: `PUT`
- **描述**: 更新账号信息
- **请求体**:
```json
{
  "password": "新密码（可选）",
  "remark": "新备注（可选）",
  "isDefault": true  // 是否设为默认账号（可选）
}
```
- **响应**: 200 OK
```json
{
  "id": 1,
  "username": "用户名",
  "remark": "新备注",
  "isDefault": true,
  "created_at": "2024-04-25T10:30:00"
}
```

### 1.5 删除账号
- **URL**: `/accounts/{account_id}`
- **方法**: `DELETE`
- **描述**: 删除账号
- **响应**: 204 No Content

## 2. 场馆查询

### 2.1 获取可用场馆
- **URL**: `/venues?serviceid={serviceid}&date={date}`
- **方法**: `GET`
- **描述**: 获取特定日期的可用场馆列表
- **参数**:
  - `serviceid`: 服务ID（数字类型）
  - `date`: 日期（格式：YYYY-MM-DD）
- **响应**: 200 OK
```json
[
  {
    "id": 1,
    "original_id": 123,
    "serviceid": 1,
    "stockid": 456,
    "date": "2024-04-25",
    "time_no": "20:01-21:00",
    "sname": "篮球场1号",
    "status": 1
  },
  {
    "id": 2,
    "original_id": 124,
    "serviceid": 1,
    "stockid": 457,
    "date": "2024-04-25",
    "time_no": "21:01-22:00",
    "sname": "篮球场2号",
    "status": 1
  }
]
```

## 3. 自动预约

### 3.1 创建自动预约任务
- **URL**: `/auto-bookings`
- **方法**: `POST`
- **描述**: 创建自动预约任务
- **请求体**:
```json
{
  "venue_id": 1,
  "account_id": 1,
  "booking_date": "2024-04-25",
  "time_no": "20:01-21:00",
  "users": "学号1/学号2"
}
```
- **响应**: 201 Created
```json
{
  "id": 1,
  "venue_id": 1,
  "account_id": 1,
  "booking_date": "2024-04-25",
  "time_no": "20:01-21:00",
  "users": "学号1/学号2",
  "status": "pending",
  "scheduled_time": "2024-04-24T08:00:05",
  "created_at": "2024-04-23T14:30:00",
  "executed_at": null,
  "result": null,
  "venue": {
    "id": 1,
    "sname": "篮球场1号",
    "time_no": "20:01-21:00"
  },
  "account": {
    "id": 1,
    "username": "用户名",
    "remark": "备注信息"
  }
}
```

### 3.2 获取自动预约任务列表
- **URL**: `/auto-bookings?status={status}`
- **方法**: `GET`
- **描述**: 获取自动预约任务列表
- **参数**:
  - `status`: 任务状态（可选，包括pending/completed/failed/cancelled）
- **响应**: 200 OK
```json
[
  {
    "id": 1,
    "venue_id": 1,
    "account_id": 1,
    "booking_date": "2024-04-25",
    "time_no": "20:01-21:00",
    "users": "学号1/学号2",
    "status": "pending",
    "scheduled_time": "2024-04-24T08:00:05",
    "created_at": "2024-04-23T14:30:00",
    "executed_at": null,
    "result": null,
    "venue": {
      "id": 1,
      "sname": "篮球场1号",
      "time_no": "20:01-21:00"
    },
    "account": {
      "id": 1,
      "username": "用户名1",
      "remark": "备注1"
    }
  },
  {
    "id": 2,
    "venue_id": 2,
    "account_id": 2,
    "booking_date": "2024-04-26",
    "time_no": "19:01-20:00",
    "users": "学号3/学号4",
    "status": "completed",
    "scheduled_time": "2024-04-25T08:00:05",
    "created_at": "2024-04-24T15:20:00",
    "executed_at": "2024-04-25T08:00:07",
    "result": { "msg": "预约成功" },
    "venue": {
      "id": 2,
      "sname": "篮球场2号",
      "time_no": "19:01-20:00"
    },
    "account": {
      "id": 2,
      "username": "用户名2",
      "remark": "备注2"
    }
  }
]
```

### 3.3 获取单个自动预约任务
- **URL**: `/auto-bookings/{booking_id}`
- **方法**: `GET`
- **描述**: 获取特定自动预约任务详情
- **响应**: 200 OK
```json
{
  "id": 1,
  "venue_id": 1,
  "account_id": 1,
  "booking_date": "2024-04-25",
  "time_no": "20:01-21:00",
  "users": "学号1/学号2",
  "status": "pending",
  "scheduled_time": "2024-04-24T08:00:05",
  "created_at": "2024-04-23T14:30:00",
  "executed_at": null,
  "result": null,
  "venue": {
    "id": 1,
    "sname": "篮球场1号",
    "time_no": "20:01-21:00"
  },
  "account": {
    "id": 1,
    "username": "用户名",
    "remark": "备注信息"
  }
}
```

### 3.4 取消自动预约任务
- **URL**: `/auto-bookings/{booking_id}`
- **方法**: `DELETE`
- **描述**: 取消自动预约任务（仅限状态为pending的任务）
- **响应**: 204 No Content

## 4. 手动预约

### 4.1 使用账号直接预约
- **URL**: `/prebook-with-account`
- **方法**: `POST`
- **描述**: 使用指定账号立即进行预约
- **请求体**:
```json
{
  "stockid": "456",
  "serviceid": "1",
  "venue_id": "123",
  "users": "学号1/学号2",
  "account_id": 1
}
```
- **响应**: 200 OK
```json
{
  "status": "success",
  "result": {
    "msg": "预约成功",
    "data": { ... }
  }
}
```

### 4.2 使用临时账号直接预约
- **URL**: `/prebook`
- **方法**: `POST`
- **描述**: 使用临时账号信息立即进行预约
- **参数**:
  - `stockid`: 库存ID
  - `serviceid`: 服务ID
  - `venue_id`: 场馆ID
  - `users`: 使用者学号（用"/"分隔多个）
  - `username`: 登录用户名
  - `password`: 登录密码
- **响应**: 200 OK
```json
{
  "status": "success",
  "result": {
    "msg": "预约成功",
    "data": { ... }
  }
}
```

## 5. 数据管理

### 5.1 导入场馆数据
- **URL**: `/import-data`
- **方法**: `POST`
- **描述**: 从源系统导入特定日期的场馆数据
- **参数**:
  - `date`: 日期（格式：YYYY-MM-DD）
  - `serviceid`: 服务ID（数字类型）
- **响应**: 200 OK
```json
{
  "imported": 15
}
```

## 状态码说明
- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `204 No Content`: 请求成功，无返回内容
- `400 Bad Request`: 请求参数错误
- `404 Not Found`: 资源不存在
- `422 Unprocessable Entity`: 请求体格式错误
- `500 Internal Server Error`: 服务器内部错误

## 注意事项
1. 创建自动预约任务时，系统会将执行时间设置为预约日期的前一天早上8:00:05
2. 自动预约任务的状态包括：pending（等待执行）、completed（已完成）、failed（失败）、cancelled（已取消）
3. 所有POST请求必须使用JSON格式的请求体，并设置Content-Type为application/json 