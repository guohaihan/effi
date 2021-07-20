from django.contrib import admin
from guozhi.models import Sqlscripts, SqlOperationLog
# Register your models here.


admin.site.register(Sqlscripts)
admin.site.register(SqlOperationLog)

