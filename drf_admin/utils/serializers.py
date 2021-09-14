# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : serializers.py
@create   : 2021/9/13 23:23
"""
from rest_framework import serializers


class MyBaseSerializer(serializers.ModelSerializer):
    """
    格式化时间的返回格式
    """
    create_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    update_time = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
