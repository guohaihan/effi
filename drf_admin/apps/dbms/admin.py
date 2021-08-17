from django.contrib import admin
from dbms.models import Sqlscripts, SqlOperationLog, DBServerConfig
# Register your models here.


admin.site.register(Sqlscripts)
admin.site.register(SqlOperationLog)
admin.site.register(DBServerConfig)
