# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : item_reports.py
@create   : 2021/12/2 13:43
"""
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from reports.models import ItemReports
from system.models import CommonConfig
from rest_framework.response import Response
from django_filters.rest_framework.filterset import FilterSet
from django_filters import filters
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from dbms.serializers.operates import OperateLogsSerializer
from django_filters.rest_framework import DjangoFilterBackend
import pymysql
import re
import base64
from Crypto.Cipher import AES
from django.conf import settings
from rest_framework.filters import SearchFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from reports.serializers.item_reports import ItemReportsSerializer
from drf_admin.utils.views import AdminViewSet
from rest_framework import status
import json
from celery_tasks.dingding.tasks import send_dingding_msg
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from openpyxl import Workbook


def score():
    pass


class ItemReportsViewSet(AdminViewSet):
    """
    list:
    审核--列表

    审核列表, status: 201(成功), return: 列表
    create:
    审核--创建

    创建审核, status: 201(成功), return: 添加信息
    update:
    审核--更新，支持局部

    进行审核操作, status: 201(成功), return: 更新后信息
    retrieve:
    审核--详情信息

    审核信息, status: 201(成功), return: 审核数据信息
    multiple_update:
    审核--批量更新，支持局部

    审核信息, status: 201(成功), return: 更新后数据信息
    multiple_delete:
    审核--批量删除

    审核信息, status: 201(成功), return: null
    destroy:
    审核--删除

    审核信息, status: 201(成功), return: null
    """
    queryset = ItemReports.objects.order_by("-update_time")
    serializer_class = ItemReportsSerializer
    # 自定义过滤字段
    filter_backends = [SearchFilter]
    search_fields = ("name", "content")
