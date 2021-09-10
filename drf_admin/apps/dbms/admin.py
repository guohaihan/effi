from django.contrib import admin
from dbms.models import Sqlscripts, OperateLogs, DBServerConfig, Audits
# Register your models here.


admin.site.register(Sqlscripts)
admin.site.register(OperateLogs)
admin.site.register(DBServerConfig)
admin.site.register(Audits)