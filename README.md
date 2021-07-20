### 项目简介
一个基于 Django、Django REST framework（DRF）、Channels、Redis、Vue的前后端分离的效率平台


####  系统功能
- 系统管理
    - 用户管理: 提供用户的相关配置及用户筛选，新增用户后，默认密码为123456
    - 角色管理: 对权限进行分配，可依据实际需要设置角色
    - 权限管理: 权限自由控制，增删改查等
    - 部门管理: 可配置系统组织架构，树形表格展示
    - 任务调度: Cron任务管理
- 系统监控
    - 在线用户: 在线用户监控
    - IP黑名单: 实现系统IP黑名单拉黑功能
    - 错误日志: 显示后台未知错误及其详情信息
    - 服务监控: 实时监控查看后台服务器性能
- 资产管理
    - 服务器管理: 服务器增删改查
- 工作管理
- 系统工具
    - 系统接口: 展示后台接口--Swagger
- 个人中心
    - 个人信息管理


#### 代码结构
```python
"""
├── celery_task                # Celery异步任务
├── docs                       # 文档
├── drf_admin                  # 项目主文件
│   ├── apps                   # 项目app
│   ├── common                 # 公共接口
│   ├── media                  # 上传文件media
│   ├── settings               # 配置文件
│   ├── utils                  # 全局工具
│   │   ├── exceptions.py      # 异常捕获
│   │   ├── middleware.py      # 中间件
│   │   ├── models.py          # 基类models文件
│   │   ├── pagination.py      # 分页配置
│   │   ├── permissions.py     # RBAC权限控制
│   │   ├── routers.py         # 视图routers
│   │   ├── swagger_schema.py  # swagger
│   │   ├── sqlscript.py           # 基类视图
│   │   └── websocket.py       # WebSocket用户验证
│   ├── routing.py             # WebSocket路由
│   ├── urls.py                # 项目根路由
│   └── wsgi.py                # wsgi
├── .gitignore                 # .gitignore文件
├── init.json                  # 数据库基础数据文件
├── LICENSE                    # LICENSE
├── manage.py                  # 项目入口、启动文件
├── README.md                  # README
└── requirements.txt           # requirements文件
"""
```

