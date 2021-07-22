from django.contrib import admin
from django.urls import include, path
from dbms.views import sqlscript, operation_log

urlpatterns = [
    path("sqlscript/sql_script/", sqlscript.SqlscriptGenericView.as_view()),
    path("sqlscript/sql_script/<pk>/", sqlscript.SqlscriptGenericAPIView.as_view()),
    path("sqlscript/sql_operate/<pk>/", sqlscript.SqlscriptOperateGenericView.as_view()),
    path("operation_log/get_database/<pk>/", operation_log.GetDatabaseView.as_view()),
    path("operation_log/operation_log/", operation_log.OperationLogGenericView.as_view(), name="log_record"),
    path("operation_log/operation_log/<pk>/", operation_log.OperationLogGenericAPIView.as_view()),
    path("operation_log/accounts/", operation_log.AccountsLogGenericView.as_view()),
    path("operation_log/accounts/<pk>/", operation_log.AccountsGenericAPIView.as_view()),
]