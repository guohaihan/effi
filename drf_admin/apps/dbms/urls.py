from django.contrib import admin
from django.urls import include, path
from dbms.views import sqlscript, db_operation, db

urlpatterns = [
    path("sqlscript/sql_script/", sqlscript.SqlscriptGenericView.as_view()),
    path("sqlscript/sql_script/<pk>/", sqlscript.SqlscriptGenericAPIView.as_view()),
    path("sqlscript/sql_operate/<pk>/", sqlscript.SqlscriptOperateGenericView.as_view()),
    path("db_operation/get_database/<pk>/", db_operation.GetDatabaseView.as_view()),
    path("db_operation/operation_log/", db_operation.OperationLogGenericView.as_view(), name="log_record"),
    path("db_operation/operation_log/<pk>/", db_operation.OperationLogGenericAPIView.as_view()),
    path("db/type/", db.DBTypeAPIView.as_view()),
    path("db/", db.DBServerConfigGenericView.as_view()),
    path("db/<pk>/", db.DBServerConfigGenericAPIView.as_view())
]