# Generated by Django 2.2.13 on 2021-07-19 08:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guozhi', '0004_auto_20210719_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='sqloperationlog',
            name='error_info',
            field=models.CharField(default=None, max_length=255, verbose_name='错误信息'),
        ),
    ]
