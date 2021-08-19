from django.db import models
from drf_admin.utils.models import BaseModel, BasePasswordModels
from django_redis import get_redis_connection


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
        db_table = 'dbms_sqlscripts'
        verbose_name = '果之sql脚本'
        verbose_name_plural = verbose_name


class OperateLogs(models.Model):
    env = models.CharField(max_length=20, verbose_name="执行环境")
    db_name = models.CharField(max_length=50, verbose_name="数据库名")
    operate_sql = models.TextField(verbose_name="执行语句")
    performer = models.CharField(max_length=20, verbose_name="执行者")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    status = models.IntegerField(choices=((0, '失败'), (1, '成功')), verbose_name='执行状态', default=1)
    error_info = models.CharField(max_length=255, default=None, verbose_name="message")

    class Meta:
        db_table = "dbms_operate_logs"
        verbose_name = "sql执行记录"
        verbose_name_plural = verbose_name


class DBServerConfig(BasePasswordModels, BaseModel):
    """服务器登录账户表"""
    env_type_choice = (
        (0, "生产"),
        (1, "测试"),
        (2, "开发"),
        (3, "演示"),
        (4, "验收")
    )
    database_type_choice = (
        (0, "mysql"),
        (1, "sqlserver")
    )
    # client_name = models.CharField(max_length=50, verbose_name="连接名称")
    db_env = models.IntegerField(choices=env_type_choice, default=1, verbose_name="环境类型")
    db_ip = models.CharField(max_length=50, verbose_name="ip地址")
    db_type = models.IntegerField(choices=database_type_choice, default=0, verbose_name="数据库类型")
    db_version = models.CharField(max_length=50,default=None, verbose_name="数据库版本",null=True)
    db_mark = models.CharField(max_length=200,default=None, verbose_name="备注",null=True, blank=True)
    db_name = models.CharField(max_length=50, default=None, verbose_name="数据库名称")
    db_username = models.CharField(max_length=32, verbose_name='登录账户')
    db_password = models.CharField(max_length=128, verbose_name='登录密码')
    db_port = models.PositiveIntegerField(verbose_name='登录端口号')
    create_user = models.CharField(max_length=20, verbose_name="创建者")
    objects = models.Manager()

    class Meta:
        db_table = 'dbms_config_info'
        verbose_name = '数据库连接信息'
        verbose_name_plural = verbose_name
        ordering = ['update_time']
