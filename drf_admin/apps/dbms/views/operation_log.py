from rest_framework.mixins import RetrieveModelMixin

from dbms.models import SqlOperationLog, Accounts
from rest_framework.response import Response
from django_filters.rest_framework.filterset import FilterSet
from django_filters import filters
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, RetrieveAPIView
from dbms.serializers.sqlserializers import SqlOperationLogSerializer, AccountsSerializer
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

class MysqlList(object):
    # mysql 端口号,注意：必须是int类型
    def __init__(self, host, user, passwd, port, db_name):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.db_name = db_name

    def select(self, sql):
        """
        执行sql命令
        :param sql: sql语句
        :return: 元祖
        """
        conn = pymysql.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            port=self.port,
            database=self.db_name,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor
        )
        try:
            cur = conn.cursor()  # 创建游标
            # conn.cursor()
            cur.execute(sql)  # 执行sql命令
            res = cur.fetchall()  # 获取执行的返回结果
            conn.commit()
            cur.close()
            conn.close()
            return res
        except Exception as e:
            conn.rollback()
            return {"error": e}

    def get_all_db(self):
        """
        获取所有数据库名
        :return: list
        """
        # 排除自带的数据库
        exclude_list = ["sys", "information_schema", "mysql", "performance_schema"]
        sql = "show databases"  # 显示所有数据库
        res = self.select(sql)
        if not res:  # 判断结果非空
            return False

        db_list = []  # 数据库列表
        for i in res:
            db_name = i['Database']
            # 判断不在排除列表时
            if db_name not in exclude_list:
                db_list.append(db_name)

        if not db_list:
            return False

        return db_list


class GetDatabaseView(APIView):
    def get_password_display(self, field_name):
        """
        AES 解密登录密码
        :return: 原明文密码
        """
        aes = AES.new(str.encode(settings.SECRET_KEY[4:20]), AES.MODE_ECB)
        return str(
            aes.decrypt(base64.decodebytes(bytes(field_name, encoding='utf8'))).rstrip(
                b'\0').decode("utf8"))

    def base(self, name):
        queryset = Accounts.objects.filter(environment=name).values()[0]
        user = queryset["username"]
        passwd = self.get_password_display(queryset["password"])
        port = queryset["port"]
        db_name = None
        host = queryset["host"]
        return {"host": host,
                "user": user,
                "passwd": passwd,
                "db_name": db_name,
                "port": port}

    def get(self, request, name):
        # 获取某个环境的数据库
        sql_data = self.base(name)
        obj = MysqlList(sql_data["host"], sql_data["user"], sql_data["passwd"], sql_data["port"], sql_data["db_name"])
        all_db_list = obj.get_all_db()
        return Response(all_db_list)

    def post(self, request, name):
        # 执行sql，并记录到日志
        base_data = self.base(name)
        # conn = get_redis_connection('user_info')
        user_info = request.user.get_user_info()
        username = user_info["username"]
        database_name = request.data["database_name"]
        sql_data = request.data["sql_data"]
        if not sql_data:
            return HttpResponse({"没有要执行的sql！"})
        if not database_name:
            return HttpResponse({"请选择要执行的数据库！"})
        pattern = re.compile(r'.*?;', re.DOTALL)
        result = pattern.findall(sql_data)
        for result_i in result:
            flag = False
            status = 1
            error_info = "null"
            for database_name_i in database_name:
                obj = MysqlList(base_data["host"], base_data["user"], base_data["passwd"], base_data["port"], database_name_i)
                sql_info = obj.select(result_i)
                if "error" in sql_info:
                    flag = True
                    status = 0
                    error_info = str(sql_info["error"])
                data = {
                    "environment": name,
                    "database_name": database_name_i,
                    "operational_data": result_i,
                    "user": username,
                    "status": status,
                    "error_info": error_info
                }
                # 将执行结果记录到日志
                OperationLogGenericView().create(data)
            if flag:
                break

        return redirect("log_record")


class MyFilterSet(FilterSet):
    # 自定义过滤字段
    operational_data = filters.CharFilter(field_name="operational_data", lookup_expr="icontains")
    status = filters.CharFilter(field_name="status", lookup_expr="icontains")

    class Meta:
        model = SqlOperationLog
        fields = ["operational_data", "status"]


class OperationLogGenericAPIView(RetrieveUpdateDestroyAPIView):
    # 获取、更新、删除某个执行日志
    queryset = SqlOperationLog.objects.order_by("-create_time")
    serializer_class = SqlOperationLogSerializer


class OperationLogGenericView(ListCreateAPIView):
    # 创建和获取执行日志
    queryset = SqlOperationLog.objects.order_by("-create_time")
    serializer_class = SqlOperationLogSerializer
    # 设置查询字段
    filter_backends = [DjangoFilterBackend]
    filter_class = MyFilterSet

    def create(self, data):
        serializer = SqlOperationLogSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)


class AccountsGenericAPIView(RetrieveUpdateDestroyAPIView):
    # 获取、更新、删除某个执行日志
    queryset = Accounts.objects.order_by("-update_time")
    serializer_class = AccountsSerializer


class AccountsLogGenericView(ListCreateAPIView):
    # 创建和获取执行日志
    queryset = Accounts.objects.order_by("-update_time")
    serializer_class = AccountsSerializer
    # 设置查询字段
    filter_backends = [DjangoFilterBackend]
