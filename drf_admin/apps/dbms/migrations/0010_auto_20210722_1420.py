# Generated by Django 2.2.13 on 2021-07-22 06:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dbms', '0009_auto_20210722_0027'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accounts',
            old_name='use',
            new_name='function',
        ),
    ]