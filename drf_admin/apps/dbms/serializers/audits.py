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
    class Meta:
        model = Audits
        fields = "__all__"
