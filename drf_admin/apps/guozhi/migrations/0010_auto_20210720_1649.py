# Generated by Django 2.2.13 on 2021-07-20 08:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guozhi', '0009_auto_20210720_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sqloperationlog',
            name='status',
            field=models.IntegerField(choices=[(0, '失败'), (1, '成功')], verbose_name='执行状态'),
        ),
    ]
