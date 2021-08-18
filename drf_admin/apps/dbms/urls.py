from django.contrib import admin
from django.urls import include, path
from dbms.views import sqlscript, operates, db

urlpatterns = [
    # path("sqlscript/sql_script/", sqlscript.SqlscriptGenericView.as_view()),
    # path("sqlscript/sql_script/<pk>/", sqlscript.SqlscriptGenericAPIView.as_view()),
    # path("sqlscript/sql_operate/<pk>/", sqlscript.SqlscriptOperateGenericView.as_view()),
    path("operates/databases/<pk>/", operates.DatabasesView.as_view()),
    path("operates/logs/", operates.OperateLogsView.as_view(), name="log_record"),
    path("operates/logs/<pk>/", operates.OperateLogsPkView.as_view()),
    path("db/type/", db.DBTypeAPIView.as_view()),
    path("db/", db.DBServerConfigGenericView.as_view()),
    path("db/<pk>/", db.DBServerConfigGenericAPIView.as_view())
]