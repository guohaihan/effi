from rest_framework import status
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, RetrieveAPIView
from drf_admin.common.file_operations import FileOperations
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework.filterset import FilterSet
from django_filters import filters
from dbms.serializers.operates import SqlscriptsSerializer
from dbms.models import Sqlscripts
import os, subprocess
# Create your views here.
from rest_framework import viewsets


class MyFilterSet(FilterSet):
    # 自定义过滤字段
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    type_id = filters.NumberFilter(field_name="type", lookup_expr="icontains")

    class Meta:
        model = Sqlscripts
        fields = ["name", "type"]


class SqlscriptGenericAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Sqlscripts.objects.order_by("-create_time")
    serializer_class = SqlscriptsSerializer


class SqlscriptGenericView(ListCreateAPIView):
    queryset = Sqlscripts.objects.order_by("-create_time")
    serializer_class = SqlscriptsSerializer
    # 设置查询字段
    filter_backends = [DjangoFilterBackend]
    filter_class = MyFilterSet


class SqlscriptOperateGenericView(RetrieveAPIView):
    queryset = Sqlscripts.objects.order_by("-create_time")
    serializer_class = SqlscriptsSerializer

    def get(self, request, *args, **kwargs):
        p = request.query_params
        instance = self.get_object()
        try:
            # 读取文件数据
            # with instance.content.open('r') as f:
            # 上传文件开头需备注：# coding=utf8
            with open(instance.content.path, 'r', encoding="utf-8") as f:
                lines = f.read()
        except Exception as e:
            return Response({'error': '%s' % e}, status=444)

        try:
            # 将文件数据写入到文件中
            with open("%s.txt" % instance.name, "w", encoding="utf-8") as f:
                f.write(lines)
        except Exception as e:
            return Response({"error": "%s" % e})

        key_list = []
        for k in p:
            key_list.append(k)
        value_list = []
        for v in key_list:
            value_list.append(p.get(v))
        # 将请求参数进行存储
        c = " ".join(value_list)
        try:
            # 执行文本
            sp = subprocess.Popen("sh %s.txt %s" % (instance.name, c), shell=True)
            sp.wait()
        except Exception as e:
            # 文件执行之后，删除文件
            if os.path.exists("%s.txt" % instance.name):
                os.remove("%s.txt" % instance.name)
            return Response({"error": "%s" % e})
        # 文件执行之后，删除文件
        if os.path.exists("%s.txt" % instance.name):
            os.remove("%s.txt" % instance.name)
        return Response({"msg": "success"})
