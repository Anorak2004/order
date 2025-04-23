# 安装与部署

本文档详细介绍系统的安装、配置和部署过程。

## 系统要求

- Python 3.6+
- SQLite 3
- 操作系统：Windows/Linux/MacOS

## 依赖安装

1. 克隆项目源码（或下载压缩包并解压）

```bash
git clone <项目仓库地址>
cd order
```

2. 创建并激活虚拟环境（推荐）

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/MacOS
python3 -m venv .venv
source .venv/bin/activate
```

3. 安装依赖包

```bash
pip install -r requirements.txt
```

系统依赖的主要包包括：
- requests
- fastapi
- sqlalchemy
- uvicorn（FastAPI的ASGI服务器）
- schedule

## 数据库配置

系统使用SQLite数据库，默认数据库文件位于`data/reservation.db`。首次运行时会自动创建数据库文件和表结构。

如需手动初始化数据库：

```bash
# 确保data目录存在
mkdir -p data
# 运行main.py时会自动创建数据库
python main.py
```

## 系统配置

### 基本配置

主要配置文件是`config.py`，包含了系统的核心配置参数：

```python
# 登录信息配置
LOGIN_DATA = {
    'dlm': '<学号>',
    'mm': '<密码>',
    'yzm': '1',
    'logintype': 'sno',
    'continueurl': '',
    'openid': ''
}

# 预约时间规则
BOOKING_HOURS = (8, 23)  # 允许预约的时间段

# 定时任务时间
SCHEDULE_TIME = "08:00"  # 每天8点执行
```

### 预约配置

预约相关配置可通过`config_setup.py`脚本进行交互式设置，也可直接编辑配置文件：

```python
# 预约参数配置
BOOKING_DATA = {
    'serviceid': '<场馆类型ID>',  # 例如：22
    'users': '<随行人员ID>',      # 例如：160734
    'stockid': '<库存ID>',       # 例如：10382
    'stockdetail_id': '<详细库存ID>' # 例如：144995
}
```

## 部署方式

### 开发环境运行

```bash
# 启动API服务
python main.py

# 运行命令行工具
python cli.py

# 启动自动预约任务
python scheduler.py
```

### 生产环境部署

#### 使用Systemd服务（Linux）

1. 创建服务文件

```bash
sudo nano /etc/systemd/system/venue-reservation.service
```

2. 添加以下内容：

```
[Unit]
Description=Venue Reservation System
After=network.target

[Service]
User=<your_username>
WorkingDirectory=/path/to/project
ExecStart=/path/to/project/.venv/bin/python main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

3. 启动服务

```bash
sudo systemctl enable venue-reservation.service
sudo systemctl start venue-reservation.service
```

#### 使用Docker部署

1. 创建Dockerfile

```
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

2. 构建并运行Docker镜像

```bash
docker build -t venue-reservation .
docker run -d -p 8000:8000 venue-reservation
```

## 验证安装

安装完成后，您可以通过以下方式验证系统是否正常工作：

1. 访问API文档
   - 启动服务后，访问 http://localhost:8000/api/docs

2. 测试数据库连接
   - 访问 http://localhost:8000/api/v1/debug/connection

3. 测试场馆查询
   - 运行 `python cli.py` 并按提示输入日期和场馆类型

## 常见问题

### 依赖安装失败

问题：安装依赖包时出现错误
解决：尝试使用国内镜像源安装

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 数据库错误

问题：无法连接到数据库
解决：检查data目录权限，确保应用有读写权限

### 登录失败

问题：无法登录到原系统
解决：检查config.py中的LOGIN_DATA配置，确保账号密码正确

## 升级指南

当有新版本发布时，按以下步骤升级：

1. 备份数据库文件
   ```bash
   cp data/reservation.db data/reservation.db.bak
   ```

2. 更新代码
   ```bash
   git pull
   ```

3. 更新依赖
   ```bash
   pip install -r requirements.txt
   ```

4. 重启服务
   ```bash
   # 如果使用systemd
   sudo systemctl restart venue-reservation.service
   
   # 如果直接运行
   python main.py
   ``` 