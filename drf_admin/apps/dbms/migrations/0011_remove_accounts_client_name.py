# Generated by Django 2.2.13 on 2021-08-08 14:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbms', '0010_auto_20210722_1420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accounts',
            name='client_name',
        ),
    ]
