# 常见问题

本文档收集了使用系统过程中的常见问题及解答。

## 系统设置问题

### Q: 如何配置自动预约的场馆和时间?

A: 您需要编辑`config_setup.py`文件，设置预约参数（如场馆类型ID、场地编号、随行人员等），然后在`config.py`中设置预约执行时间（SCHEDULE_TIME）和预约时间规则（BOOKING_HOURS）。详细步骤请参考[使用指南](usage.md)中的"自动预约"部分。

### Q: 我需要修改系统的数据库连接信息，应该怎么做?

A: 数据库连接信息在`main.py`文件中配置。默认使用SQLite数据库，连接字符串为`sqlite:///./data/reservation.db`。如果需要修改，请更新该文件中的以下代码：

```python
engine = create_engine('sqlite:///./data/reservation.db', connect_args={"check_same_thread": False})
```

### Q: 如何添加新的场馆类型?

A: 系统可以自动适配不同的场馆类型，只需要知道对应的serviceid即可。使用时，在CLI或API中指定不同的serviceid参数即可查询和预约不同类型的场馆。

## 预约问题

### Q: 为什么我的预约总是失败，提示"未到该日期的预订时间"?

A: 这通常意味着当前时间不在目标场馆的开放预约时间内。南京医科大学场馆预约系统有特定的预约规则，某些场馆可能只允许在特定时间段内预约。请检查场馆的预约规则，并在允许的时间内尝试预约。

### Q: 预约时提示"每日限预约一场"，如何解决?

A: 根据学校规定，同一用户每天只能预约一场场馆。如果您已经预约了一场，就无法在同一天预约另一场。您需要等到第二天才能继续预约。

### Q: 如何查看我已经预约的场馆?

A: 目前系统仅支持创建预约，不提供查询已预约场馆的功能。您可以通过原系统（http://order.njmu.edu.cn:8088）登录后查看您的预约记录。

### Q: 如何取消已经预约的场馆?

A: 当前系统不支持取消预约功能。如需取消预约，请登录原系统（http://order.njmu.edu.cn:8088）进行操作。

## 数据问题

### Q: 系统显示无法获取场馆数据，可能是什么原因?

A: 可能的原因包括：
1. 网络连接问题，无法访问外部API
2. 输入的日期格式不正确（应为YYYY-MM-DD）
3. 指定日期的场馆数据尚未在外部系统中开放
4. 外部系统API发生变化

请检查网络连接，确认日期格式正确，并验证外部系统是否可以访问。

### Q: JSON数据文件保存在哪里?

A: 系统从外部API获取的数据会保存在`data`目录下，文件命名格式为`service_data_{serviceid}_{date}.json`。例如：`data/service_data_22_2024-04-01.json`。

### Q: 如何手动导入数据?

A: 您可以使用系统提供的API接口导入数据：

```bash
curl -X POST "http://localhost:8000/api/v1/import-data" \
  -H "Content-Type: application/json" \
  -d '{"date": "2024-04-01", "serviceid": 22}'
```

或者通过Python脚本：

```python
from fetch_data import FetchData, DataImporter
from sqlalchemy.orm import Session
from main import SessionLocal

# 获取数据
date = "2024-04-01"
serviceid = 22
data = FetchData.fetch_service_data(date, serviceid)

# 保存并导入
if data:
    FetchData.save_data_to_json(data, date, serviceid)
    DataImporter(SessionLocal()).import_from_json(f"data/service_data_{serviceid}_{date}.json")
```

## 系统运行问题

### Q: 定时任务不执行，可能是什么原因?

A: 可能的原因包括：
1. 程序未在运行中（确保`scheduler.py`处于运行状态）
2. 系统时间不正确（检查服务器时间）
3. 配置的执行时间格式不正确（应为"HH:MM"格式）
4. 当前时间不在允许预约的时间范围内（由BOOKING_HOURS控制）

### Q: 如何让定时任务在后台运行?

A: 在Linux系统上，您可以使用以下命令让程序在后台运行：

```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

对于Windows系统，可以考虑使用Windows任务计划程序或创建系统服务。

### Q: 我的系统在启动时报错，找不到模块，如何解决?

A: 这通常是因为缺少必要的依赖包。请确保已经安装了所有必要的依赖：

```bash
pip install -r requirements.txt
```

如果`requirements.txt`中缺少某些包，您可能需要手动安装：

```bash
pip install requests fastapi sqlalchemy uvicorn schedule
```

### Q: 系统如何处理日志?

A: 目前系统主要使用标准输出（print语句）记录运行状态。如果需要保存日志，可以在运行命令时重定向输出：

```bash
python scheduler.py > logs/scheduler.log 2>&1
```

## API问题

### Q: API服务默认运行在哪个端口?

A: API服务默认运行在8000端口。如果需要修改端口，您可以在启动命令中指定：

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Q: 如何访问API文档?

A: 启动服务后，访问以下URL查看API文档：
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Q: API请求返回500错误，如何排查?

A: 500错误表示服务器内部错误。可能的原因包括：
1. 数据库连接问题
2. 代码异常
3. 外部服务不可用

检查服务器日志以获取更详细的错误信息，并确保数据库和外部服务正常运行。

## 安全问题

### Q: 系统中的密码是如何存储的?

A: 当前系统直接在配置文件中明文存储密码，这不是最佳实践。在生产环境中，建议将敏感信息如密码移至环境变量或安全存储服务。

### Q: API接口是否需要认证?

A: 当前API接口不需要认证即可访问。如需增加安全性，可以考虑添加基本认证、API密钥或OAuth等认证机制。

### Q: 如何保护我的预约数据?

A: 建议采取以下措施保护数据：
1. 使用防火墙限制API服务的访问范围
2. 定期备份数据库文件
3. 不要在公共场所运行CLI工具
4. 避免将登录凭证分享给他人

## 其他问题

### Q: 系统支持哪些操作系统?

A: 系统使用Python开发，理论上支持所有主流操作系统，包括Windows、Linux和MacOS。但建议在Linux环境下运行生产服务。

### Q: 如何贡献代码或报告问题?

A: 您可以联系系统管理员报告问题或提出功能建议。如果您有权限访问源代码仓库，可以提交Pull Request贡献代码。

### Q: 如何扩展系统功能?

A: 系统采用模块化设计，您可以通过以下方式扩展功能：
1. 在`routers.py`中添加新的API端点
2. 在`repositories.py`中扩展数据访问层
3. 创建新的工具模块实现特定功能
4. 修改`book.py`以支持更复杂的预约逻辑

详细的扩展指南请参考[模块说明](modules.md)文档。 