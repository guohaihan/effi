from dbms.models import OperateLogs, DBServerConfig, Audits
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
from dbms.serializers.audits import AuditsSerializer
from drf_admin.utils.views import AdminViewSet
from rest_framework import status
import json


class MysqlList(object):
    # mysql 端口号,注意：必须是int类型
    def __init__(self, host, user, passwd, port, db_name):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.db_name = db_name

    def execute_sql(self, sql):
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
        cur = conn.cursor()  # 创建游标
        try:
            if isinstance(sql, str):
                cur.execute(sql)  # 执行sql命令
            else:
                for sql_i in sql:
                    cur.execute(sql_i)
        except Exception as e:
            conn.rollback()
            return {"error": "sql执行失败！失败原因：%s" % e}
        else:
            res = cur.fetchall()  # 获取执行的返回结果
            conn.commit()
            cur.close()
            conn.close()
            return res

    def get_all_db(self):
        """
        获取所有数据库名
        :return: list
        """
        # 排除自带的数据库
        exclude_list = ["sys", "information_schema", "mysql", "performance_schema"]
        sql = "show databases"  # 显示所有数据库
        res = self.execute_sql(sql)
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
            environment = DBServerConfig.objects.filter(id=pk)[0].get_db_env_display()
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

    @swagger_auto_schema(responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        title="请求体",
        properties={
            "data": openapi.Schema(
                title="此请求体用审核通过后的响应data，格式为{'data': data}",
                type=openapi.TYPE_STRING,
            ),
        },
        required=["请求体"]
    )})
    def post(self, request):
        # 执行sql，并记录到日志
        if "db" not in request.data or "excute_db_name" not in request.data or "operate_sql" not in request.data:
            return Response(status=400, data={"error": "请求体错误！"})
        if not request.data["db"] or not request.data["excute_db_name"] or not request.data["operate_sql"]:
            return Response(status=400, data={"error": "请求体不允许存在value为空的参数！"})
        base_data = self.base(request.data["db"])
        if "error" in base_data:
            return Response(status=400, data={"error": base_data["error"]})
        # conn = get_redis_connection('user_info')
        if "user" in request.data:
            username = request.data["user"]
        else:
            username = request.user.get_username()
        if isinstance(request.data["excute_db_name"], list):
            database_name = request.data["excute_db_name"]
        else:
            database_name = eval(request.data["excute_db_name"])
        sql_data = request.data["operate_sql"]
        pattern = re.compile(r'.*?;', re.DOTALL)
        result = pattern.findall(sql_data)
        if not result:
            return Response(status=400, data={"error": "sql缺少';'号！"})
        sprint = None
        if "sprint" in request.data:
            sprint = request.data["sprint"]
        # 遍历数据库
        for database_name_i in database_name:
            status = 1
            error_info = ""
            obj = MysqlList(base_data["host"], base_data["user"], base_data["passwd"], base_data["port"],
                            database_name_i)
            # 执行sql操作
            sql_info = obj.execute_sql(result)
            if "error" in sql_info:
                status = 0
                error_info = str(sql_info["error"])
            data = {
                "env": base_data["environment"],
                "db_name": database_name_i,
                "operate_sql": str(result),
                "performer": username,
                "status": status,
                "error_info": error_info,
                "sprint": sprint
            }
            # 将执行结果记录到日志
            OperateLogsView().create(data)
            if error_info:
                return Response(status=400, data={"error": error_info})
        return Response("恭喜你，全部sql执行成功！")


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
    search_fields = ("operate_sql", "db_name", "sprint")

    def create(self, data, **kwargs):
        serializer = OperateLogsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)


class AuditsViewSet(AdminViewSet):
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
    queryset = Audits.objects.order_by("-update_time")
    serializer_class = AuditsSerializer
    # 自定义过滤字段
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ["status"]
    search_fields = ("sprint",)

    def create(self, request, *args, **kwargs):
        if "excute_db_name" in request.data:
            request.data["excute_db_name"] = json.dumps(request.data["excute_db_name"])
        user = request.user.get_username()
        request.data["user"] = user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def multiple_update(self, request, *args, **kwargs):
        if "excute_db_name" in request.data:
            request.data["excute_db_name"] = json.dumps(request.data["excute_db_name"])
        auditor = request.user.get_username()
        request.data["auditor"] = auditor
        return super().multiple_update(request, *args, **kwargs)

    def update(self, request, pk=None, *args, **kwargs):
        if "excute_db_name" in request.data:
            request.data["excute_db_name"] = json.dumps(request.data["excute_db_name"])
        auditor = request.user.get_username()
        request.data["auditor"] = auditor
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)