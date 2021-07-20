from django.db import models
from drf_admin.utils.models import BaseModel


class Sqlscripts(BaseModel):
    type_choices = (
        (1, "sql"),
        (2, "shell")
    )
    name = models.CharField(max_length=50, unique=True, verbose_name="名称")
    type = models.CharField(max_length=10, choices=type_choices, verbose_name="类型")
    content = models.FileField(upload_to="files", verbose_name="文件内容")
    creator = models.CharField(max_length=20, verbose_name="创建者")

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'guozhi_sqlscripts'
        verbose_name = '果之sql脚本'
        verbose_name_plural = verbose_name


class SqlOperationLog(models.Model):
    environment = models.CharField(max_length=20, verbose_name="环境")
    database_name = models.CharField(max_length=50, verbose_name="数据库名")
    operational_data = models.TextField(verbose_name="执行语句")
    user = models.CharField(max_length=20, verbose_name="用户名")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    status = models.IntegerField(choices=((0, '失败'), (1, '成功')), verbose_name='执行状态', default=1)
    error_info = models.CharField(max_length=255, default="Null", verbose_name="错误信息")

    class Meta:
        db_table = "guozhi_operation_log"
        verbose_name = "sql执行记录"
        verbose_name_plural = verbose_name
