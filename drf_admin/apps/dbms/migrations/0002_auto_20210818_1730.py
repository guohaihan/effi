# Generated by Django 2.2.13 on 2021-08-18 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperateLogs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('env', models.CharField(max_length=20, verbose_name='环境')),
                ('db_name', models.CharField(max_length=50, verbose_name='数据库名')),
                ('operate_sql', models.TextField(verbose_name='执行语句')),
                ('performer', models.CharField(max_length=20, verbose_name='执行者')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('status', models.IntegerField(choices=[(0, '失败'), (1, '成功')], default=1, verbose_name='执行状态')),
                ('error_info', models.CharField(default=None, max_length=255, verbose_name='message')),
            ],
            options={
                'verbose_name': 'sql执行记录',
                'verbose_name_plural': 'sql执行记录',
                'db_table': 'dbms_operate_logs',
            },
        ),
        migrations.DeleteModel(
            name='SqlOperationLog',
        ),
        migrations.AlterField(
            model_name='dbserverconfig',
            name='db_mark',
            field=models.CharField(blank=True, default=None, max_length=200, null=True, verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='dbserverconfig',
            name='db_version',
            field=models.CharField(default=None, max_length=50, null=True, verbose_name='数据库版本'),
        ),
    ]
