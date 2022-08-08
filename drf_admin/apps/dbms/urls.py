from django.urls import path
from dbms.views import operates, db, desensitises
from drf_admin.utils.routers import AdminRouter

router = AdminRouter()
router.register(r'audits', operates.AuditsViewSet, basename='audits')
urlpatterns = router.urls
urlpatterns += [
    # path("sqlscript/sql_script/", sqlscript.SqlscriptGenericView.as_view()),
    # path("sqlscript/sql_script/<pk>/", sqlscript.SqlscriptGenericAPIView.as_view()),
    # path("sqlscript/sql_operate/<pk>/", sqlscript.SqlscriptOperateGenericView.as_view()),
    path("operates/excel/", operates.export_excel),  # 数据查询结果导出
    path("operates/check/", operates.check),  # 进行sql检查
    path("operates/databases/", operates.DatabasesView.as_view()),  # 执行sql
    path("operates/databases/<pk>/", operates.DatabasesView.as_view()),  # 查询数据库
    path("operates/logs/", operates.OperateLogsView.as_view()),  # 操作日志
    path("operates/logs/<pk>/", operates.OperateLogsPkView.as_view()),  # 查看操作日志详情
    path("db/type/", db.DBTypeAPIView.as_view()),
    path("db/", db.DBServerConfigGenericView.as_view()),  # 获取数据库环境：列表和创建
    path("db/<pk>/", db.DBServerConfigGenericAPIView.as_view()),  # 获取某个数据库：详情、更改、删除
    path("desensitises/config/", desensitises.config),  # 数据库脱敏设置
]