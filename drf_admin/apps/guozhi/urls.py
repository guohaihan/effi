from django.contrib import admin
from django.urls import include, path
from guozhi.views import sqlscript, operation_log

urlpatterns = [
    path("sqls/", sqlscript.SqlscriptGenericView.as_view()),
    path("sqls/<pk>/", sqlscript.SqlscriptGenericAPIView.as_view()),
    path("operate/<pk>/", sqlscript.SqlscriptOperateGenericView.as_view()),
    path("logs/<str:name>/", operation_log.GetDatabaseView.as_view()),
    path("logs/record/list/", operation_log.OperationLogGenericView.as_view(), name="log_record"),
    path("logs/record/<pk>/", operation_log.OperationLogGenericAPIView.as_view()),
]