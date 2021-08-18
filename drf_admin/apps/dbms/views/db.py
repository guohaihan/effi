from rest_framework import mixins
from rest_framework.mixins import RetrieveModelMixin

from dbms.models import DBServerConfig
from rest_framework.response import Response
from django_filters.rest_framework.filterset import FilterSet
from django_filters import filters
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, RetrieveAPIView
from dbms.serializers.dbs import DBServerConfigSerializer
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
import pymysql
import re
import json
import requests
from django.shortcuts import redirect
from django.urls import reverse
from django_redis import get_redis_connection
from drf_admin.utils.models import BaseModel, BasePasswordModels
import base64
from Crypto.Cipher import AES
from django.conf import settings
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_admin.utils.views import ChoiceAPIView


class DBServerConfigGenericAPIView(RetrieveUpdateDestroyAPIView):
    """
    get:
    数据库--详情信息

    获取数据库, status: 201(成功), return: 服务器信息
    put:
    数据库--更新信息

    数据库更新, status: 201(成功), return: 更新后信息

    patch:
    数据库--更新信息

    数据库更新, status: 201(成功), return: 更新后信息

    delete:
    数据库--删除

    数据库删除, status: 201(成功), return: None
    """
    # 获取、更新、删除某个数据库信息
    queryset = DBServerConfig.objects.order_by("-update_time")
    serializer_class = DBServerConfigSerializer

    def put(self, request, *args, **kwargs):
        if len(request.data) < 9:
            kwargs['partial'] = True
        username = request.user.get_username()
        request.data["create_user"] = username
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)


class DBServerConfigGenericView(ListCreateAPIView):
    """
    get:
    数据库--列表

    数据库列表, status: 201(成功), return: 列表
    post:
    数据库--创建

    数据库创建, status: 201(成功), return: 服务器信息
    """
    # 创建和获取数据库信息
    queryset = DBServerConfig.objects.order_by("-update_time")
    serializer_class = DBServerConfigSerializer
    # 自定义过滤字段
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ['db_type', "db_env"]
    search_fields = ("db_ip", "db_name")

    def post(self, request, *args, **kwargs):
        username = request.user.get_username()
        request.data["create_user"] = username
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, headers=headers)


class DBTypeAPIView(ChoiceAPIView):
    """
    get:
    数据库-models类型列表

    数据库models中的类型列表信息, status: 200(成功), return: 服务器models中的类型列表
    """
    choice = DBServerConfig.database_type_choice


