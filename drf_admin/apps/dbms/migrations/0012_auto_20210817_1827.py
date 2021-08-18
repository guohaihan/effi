# Generated by Django 2.2.13 on 2021-08-17 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbms', '0011_remove_accounts_client_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DBServerConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('db_env', models.IntegerField(choices=[(0, '生产'), (1, '测试'), (2, '开发'), (3, '演示'), (4, '验收')], default=1, verbose_name='环境类型')),
                ('db_ip', models.CharField(max_length=50, verbose_name='ip地址')),
                ('db_type', models.IntegerField(choices=[(0, 'mysql'), (1, 'sqlserver')], default=0, verbose_name='数据库类型')),
                ('db_version', models.CharField(max_length=50, verbose_name='数据库版本')),
                ('db_mark', models.CharField(max_length=200, verbose_name='备注')),
                ('db_name', models.CharField(default=None, max_length=50, verbose_name='数据库名称')),
                ('db_username', models.CharField(max_length=32, verbose_name='登录账户')),
                ('db_password', models.CharField(max_length=64, verbose_name='登录密码')),
                ('db_port', models.PositiveIntegerField(verbose_name='登录端口号')),
                ('create_user', models.CharField(max_length=20, verbose_name='创建者')),
            ],
            options={
                'verbose_name': '数据库连接信息',
                'verbose_name_plural': '数据库连接信息',
                'db_table': 'db_config_info',
                'ordering': ['update_time'],
            },
        ),
        migrations.DeleteModel(
            name='Accounts',
        ),
    ]