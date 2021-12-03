from django.contrib import admin
from reports.models import ItemReports, Story, ToDo, Score, BugClass
# Register your models here.


admin.site.register(ItemReports)
admin.site.register(Story)
admin.site.register(ToDo)
admin.site.register(Score)
admin.site.register(BugClass)
