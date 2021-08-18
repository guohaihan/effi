from django.contrib import admin
from dbms.models import Sqlscripts, OperateLogs, DBServerConfig
# Register your models here.


admin.site.register(Sqlscripts)
admin.site.register(OperateLogs)
admin.site.register(DBServerConfig)
