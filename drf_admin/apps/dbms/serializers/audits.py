# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : audits.py
@create   : 2021/8/26 16:11
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from dbms.models import Audits


class AuditsSerializer(serializers.ModelSerializer):
    # 添加额外字段
    db_env = serializers.SerializerMethodField(label="执行环境")
    db_name = serializers.SerializerMethodField(label="数据库名称")

    class Meta:
        model = Audits
        fields = "__all__"

    def get_db_env(self, obj):
        return obj.db.get_db_env_display()

    def get_db_name(self, obj):
        return obj.db.db_name
