from dbms.models import OperateLogs, DBServerConfig
from rest_framework.response import Response
from django_filters.rest_framework.filterset import FilterSet
from django_filters import filters
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, RetrieveAPIView
from dbms.serializers.operates import OperateLogsSerializer
from django_filters.rest_framework import DjangoFilterBackend
import pymysql
import re
from django.shortcuts import redirect
import base64
from Crypto.Cipher import AES
from django.conf import settings
from rest_framework.filters import SearchFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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
        try:
            conn = pymysql.connect(
                host=self.host,
                user=self.user,
                passwd=self.passwd,
                port=self.port,
                database=self.db_name,
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor
            )
        except Exception as e:
            return {"error": "连接数据库失败！失败原因：%s" % e}
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
            return {"error": "sql执行失败！失败原因：%s" % e}

    def get_all_db(self):
        """
        获取所有数据库名
        :return: list
        """
        # 排除自带的数据库
        exclude_list = ["sys", "information_schema", "mysql", "performance_schema"]
        sql = "show databases"  # 显示所有数据库
        res = self.select(sql)
        if "error" in res:  # 判断结果非空
            return res

        if not res:
            return {"error": "数据库为空！"}
        for i in res:
            db_name = i['Database']
            # 判断不在排除列表时
            if db_name in exclude_list:
                res.remove(i)
        return res


class DatabasesView(APIView):
    """
    get:
    数据库操作--连接数据库

    获取信息详情, status: 201(成功), return: 数据库表
    post:
    数据库操作--执行sql

    获取信息详情, status: 201(成功), return: 执行结果
    """

    def get_password_display(self, field_name):
        """
        AES 解密登录密码
        :return: 原明文密码
        """
        aes = AES.new(str.encode(settings.SECRET_KEY[4:20]), AES.MODE_ECB)
        return str(
            aes.decrypt(base64.decodebytes(bytes(field_name, encoding='utf8'))).rstrip(
                b'\0').decode("utf8"))

    def base(self, pk):
        """
        拼接数据库连接信息
        """
        try:
            queryset = DBServerConfig.objects.filter(id=pk).values()[0]
            user = queryset["db_username"]
            passwd = self.get_password_display(queryset["db_password"])
            port = queryset["db_port"]
            db_name = None
            host = queryset["db_ip"]
            environment = queryset["db_env"]
        except:
            return {"error": "获取数据库连接的基本信息失败！"}
        return {
            "host": host,
            "user": user,
            "passwd": passwd,
            "db_name": db_name,
            "port": port,
            "environment": environment
        }

    @swagger_auto_schema(responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="db_info",
        properties={
            "Database": openapi.Schema(
                title="Database",
                type=openapi.TYPE_STRING,
            ),
        },
        required=["Database"]
    )})
    def get(self, request, pk):
        base_data = self.base(pk)
        if "error" in base_data:
            return Response(status=400, data={"error": base_data["error"]})
        # 获取某个环境的数据库
        obj = MysqlList(base_data["host"], base_data["user"], base_data["passwd"], base_data["port"], base_data["db_name"])
        all_db_list = obj.get_all_db()
        if "error" in all_db_list:
            return Response(status=400, data={"error": all_db_list["error"]})
        return Response(all_db_list)

    @swagger_auto_schema(request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="Operate_sql",
            properties={
                "db_name": openapi.Schema(
                    title="db_name",
                    type=openapi.TYPE_STRING,
                    description="将db_name放在列表中传递"
                ),
                "operate_sql": openapi.Schema(
                    title="operate_sql",
                    type=openapi.TYPE_STRING,
                ),
            },
            required=["db_name", "operate_sql"]
    ))
    def post(self, request, pk):
        # 执行sql，并记录到日志
        base_data = self.base(pk)
        if "error" in base_data:
            return Response(status=400, data={"error": base_data["error"]})
        # conn = get_redis_connection('user_info')
        username = request.user.get_username()
        database_name = request.data["db_name"]
        sql_data = request.data["operate_sql"]
        if not sql_data:
            return Response(status=400, data={"error": "没有要执行的sql"})
        if not database_name:
            return Response(status=400, data={"error": "请选择要执行的数据库！"})
        pattern = re.compile(r'.*?;', re.DOTALL)
        result = pattern.findall(sql_data)
        if not result:
            return Response(status=400, data={"error": "sql缺少';'号！"})
        for result_i in result:
            status = 1
            error_info = ""
            for database_name_i in database_name:
                obj = MysqlList(base_data["host"], base_data["user"], base_data["passwd"], base_data["port"], database_name_i)
                sql_info = obj.select(result_i)
                if "error" in sql_info:
                    status = 0
                    error_info = str(sql_info["error"])
                data = {
                    "env": base_data["environment"],
                    "db_name": database_name_i,
                    "operate_sql": result_i,
                    "performer": username,
                    "status": status,
                    "error_info": error_info
                }
                # 将执行结果记录到日志
                OperateLogsView().create(data)
                if error_info:
                    break
            if error_info:
                break

        return redirect("log_record")


class MyFilterSet(FilterSet):
    # 自定义过滤字段
    operational_data = filters.CharFilter(field_name="operate_sql", lookup_expr="icontains")
    status = filters.CharFilter(field_name="status", lookup_expr="icontains")

    class Meta:
        model = OperateLogs
        fields = ["operate_sql", "status"]


class OperateLogsPkView(RetrieveAPIView):
    """
    get:
    数据库执行日志--详情信息

    获取信息详情, status: 201(成功), return: 日志详情
    """
    # 获取某个执行日志详情
    queryset = OperateLogs.objects.order_by("-create_time")
    serializer_class = OperateLogsSerializer


class OperateLogsView(ListCreateAPIView):
    """
    get:
    数据库执行日志--列表

    日志列表, status: 201(成功), return: 列表
    post:
    数据库执行日志--创建

    创建日志, status: 201(成功), return: 日志信息
    """
    # 创建和获取执行日志
    queryset = OperateLogs.objects.order_by("-create_time")
    serializer_class = OperateLogsSerializer
    # 自定义过滤字段
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ['status', "env"]
    search_fields = ("operate_sql", "db_name")

    def create(self, data, **kwargs):
        serializer = OperateLogsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)
