from django.contrib import admin
from dbms.models import Sqlscripts, SqlOperationLog, Accounts
# Register your models here.


admin.site.register(Sqlscripts)
admin.site.register(SqlOperationLog)
admin.site.register(Accounts)
