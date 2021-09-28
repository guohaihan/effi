from django.urls import include, path
from dbms.views import sqlscript, operates, db
from drf_admin.utils.routers import AdminRouter

router = AdminRouter()
router.register(r'audits', operates.AuditsViewSet, basename='audits')
urlpatterns = router.urls
urlpatterns += [
    # path("sqlscript/sql_script/", sqlscript.SqlscriptGenericView.as_view()),
    # path("sqlscript/sql_script/<pk>/", sqlscript.SqlscriptGenericAPIView.as_view()),
    # path("sqlscript/sql_operate/<pk>/", sqlscript.SqlscriptOperateGenericView.as_view()),
    path("operates/excel/", operates.export_excel),
    path("operates/databases/", operates.DatabasesView.as_view()),
    path("operates/databases/<pk>/", operates.DatabasesView.as_view()),
    path("operates/logs/", operates.OperateLogsView.as_view()),
    path("operates/logs/<pk>/", operates.OperateLogsPkView.as_view()),
    path("db/type/", db.DBTypeAPIView.as_view()),
    path("db/", db.DBServerConfigGenericView.as_view()),
    path("db/<pk>/", db.DBServerConfigGenericAPIView.as_view()),
]