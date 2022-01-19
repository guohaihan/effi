from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from dbms.models import OperateLogs, DBServerConfig, Audits
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
from dbms.serializers.audits import AuditsSerializer
from drf_admin.utils.views import AdminViewSet
from rest_framework import status
import json
from celery_tasks.dingding.tasks import send_dingding_msg
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from openpyxl import Workbook
import os
from django_redis import get_redis_connection


class MysqlList(object):
    # mysql 端口号,注意：必须是int类型
    def __init__(self, host, user, passwd, port, db_name):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.port = port
        self.db_name = db_name

    # 进行数据脱敏
    def desen(self, sql):
        """
        1，从redis中获取设置内容，不存在时，使用默认值；
        2，判断第一个select后是否有*，有则通过正则拿字段（区分有无as），无则通过sql获取字段；
        3，进行脱敏字段比对；
        4，确认sql最后是否有limit，无则使用默认值；
        """
        # redis_conn = get_redis_connection('desensitises_config')  # 连接redis，获取脱敏配置
        # desensitises = redis_conn.smembers("desensitises")
        # limit = redis_conn.get("limit")
        # desensitises_l = []
        # if desensitises:
        #     for d_i in desensitises:
        #         desensitises_l.append(d_i.decode("utf-8"))
        # if not limit:
        #     limit = 1000
        # else:
        #     limit = int(limit.decode("utf-8"))

        desensitises_l = []
        # 获取脱敏字段
        desensitises = CommonConfig.objects.filter(server="dbms", name="desensitises")
        if desensitises:
            desensitises_l = eval(desensitises.values()[0]["value"])
        # 获取限制条数
        limit = CommonConfig.objects.filter(server="dbms", name="limit")
        if limit:
            limit = eval(limit.values()[0]["value"])
        else:
            limit = 1000
        if isinstance(sql, str):
            sql = [sql]  # 如果只有一条sql，将sql放入列表
        for i in range(len(sql)):
            sql[i] = sql[i].lower().replace("\n", " ").strip()
            if sql[i].startswith("select"):
                # 查询语句没有*时
                result = re.search(r'select (.*?) from', sql[i], re.DOTALL | re.I)
                if not result:
                    return [{"sql": sql[i], "message": "FAIL，失败原因：缺少字段名；"}]
                col_name = result.group(1).split(",")
                for col_i in range(len(col_name)):
                    # 字段重命名时，是否有as
                    if " as " in col_name[col_i]:
                        col_name[col_i] = col_name[col_i].strip()
                        v_i = re.search(r'(.*?)\sas', col_name[col_i], re.DOTALL | re.I)
                        col_name[col_i] = v_i.group(1)
                        if col_name[col_i] in desensitises_l:
                            sql[i] = re.sub(r'\s%s\s' % col_name[col_i], '@%s:="*"' % col_name[col_i], sql[i], 1)
                        elif col_name[col_i].find(".") > 0:
                            col_name_index = col_name[col_i].find(".")
                            if col_name[col_i][col_name_index+1:] in desensitises_l:
                                sql[i] = re.sub(r'%s as ' % col_name[col_i], '@%s:="*" as ' % col_name[col_i].strip(), sql[i], 1)
                    # 字段重命名时，无as
                    elif re.search(r'\w+\s\w+', col_name[col_i], re.DOTALL | re.I):
                        col_name[col_i] = col_name[col_i].strip()
                        v_i = re.search(r'(.*?)\s\w', col_name[col_i], re.DOTALL | re.I)
                        col_name[col_i] = v_i.group(1)
                        if col_name[col_i] in desensitises_l:
                            sql[i] = re.sub(r'\s%s\s' % col_name[col_i], '@%s:="*"' % col_name[col_i], sql[i], 1)
                        elif col_name[col_i].find(".") > 0:
                            col_name_index = col_name[col_i].find(".")
                            if col_name[col_i][col_name_index+1:] in desensitises_l:
                                sql[i] = re.sub(r'%s' % col_name[col_i], '@%s:="*"' % col_name[col_i].strip(), sql[i], 1)
                    else:
                        col_name[col_i] = col_name[col_i].strip()
                        if col_name[col_i] in desensitises_l:
                            sql[i] = re.sub(r"%s" % col_name[col_i], "@%s:='*' as %s" % (col_name[col_i], col_name[col_i]), sql[i], 1)
                        elif col_name[col_i].find(".") > 0:
                            col_name_index = col_name[col_i].find(".")
                            if col_name[col_i][col_name_index+1:] in desensitises_l:
                                sql[i] = re.sub(r'%s' % col_name[col_i], '@%s:="*" as %s' % (col_name[col_i], col_name[col_i][col_name_index+1:]), sql[i], 1)
                # 判断有无limit，不存在时，添加limit
                result = re.search(r'.* limit [0-9]+;', sql[i], re.DOTALL|re.I)
                if not result:
                    sql[i] = sql[i].replace(";", " limit %d;" % limit)
        data = self.execute_sql(sql)  # 进行sql执行
        return data

    def execute_sql(self, sql, db_env=True):
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
        # redis_conn = get_redis_connection('desensitises_config')  # 连接redis，获取脱敏配置
        # desensitises = redis_conn.smembers("desensitises")
        # desensitises_l = []
        # if desensitises:
        #     for d_i in desensitises:
        #         desensitises_l.append(d_i.decode("utf-8"))

        desensitises_l = []
        # 获取脱敏字段
        desensitises = CommonConfig.objects.filter(server="dbms", name="desensitises")
        if desensitises:
            desensitises_l = eval(desensitises.values()[0]["value"])
        # 获取限制条数
        limit = CommonConfig.objects.filter(server="dbms", name="limit")
        if limit:
            limit = eval(limit.values()[0]["value"])
        else:
            limit = 1000

        cur = conn.cursor()  # 创建游标
        info = []
        if isinstance(sql, str):
            sql = [sql]  # 如果只有一条sql，将sql放入列表
        for sql_i in sql:
            sql_i = sql_i.lower().replace("\n", " ").strip()
            if sql_i.startswith("select"):
                # 判断有无limit，不存在时，添加limit
                result = re.search(r'.* limit [0-9]+;', sql_i, re.DOTALL|re.I)
                if not result:
                    sql_i = sql_i.replace(";", " limit %d;" % limit)
            try:
                row_count = cur.execute(sql_i)
                if sql_i.startswith("alter") or sql_i.startswith("update"):
                    info.append({"sql": sql_i, "message": "OK，影响行数：%d" % row_count})
                elif sql_i.startswith("select"):
                    res = cur.fetchall()  # 获取执行的返回结果
                    if res:
                        for key_i in list(res[0].keys()):
                            if key_i in ["create_time", "update_time"]:
                                for res_i in res:
                                    res_i[key_i] = res_i[key_i].strftime('%Y-%m-%d %H:%M:%S')
                            if not db_env and key_i in desensitises_l:
                                for res_i in res:
                                    res_i[key_i] = "*"
                    info.append({"sql": sql_i, "message": "OK，影响行数：%d" % row_count, "data": res})
                elif sql_i.startswith("show"):
                    res = cur.fetchall()  # 获取执行的返回结果
                    info.append({"sql": sql_i, "message": "OK，影响行数：%d" % row_count, "data": res})
                else:
                    info.append({"sql": sql_i, "message": "OK"})
            except Exception as e:
                conn.rollback()
                cur.close()
                conn.close()
                info.append({"sql": sql_i, "message": "FAIL，失败原因：{}".format(e)})
                return info
        conn.commit()
        cur.close()
        conn.close()
        return info

    def get_all_db(self):
        """
        获取所有数据库名
        :return: list
        """
        # 排除自带的数据库
        exclude_list = ["sys", "information_schema", "mysql", "performance_schema"]
        sql = "show databases"  # 显示所有数据库
        res = self.execute_sql(sql)
        if "FAIL" in res[-1]["message"]:
            return res

        if not res:
            return {"error": "数据库为空！"}
        res = res[-1]["data"]
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
        if request.query_params:
            # tenant用来过滤租户库
            if "tenant" not in request.query_params:
                return Response(status=400, data={"error": "请求参数为tenant"})
            for all_db_i in all_db_list[:]:
                if not all_db_i["Database"].startswith("guozhi_tenant_") or all_db_i["Database"]=="guozhi_tenant_1":
                    all_db_list.remove(all_db_i)
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
        db_env = DBServerConfig.objects.filter(id=request.data["db"]).values()[0]["db_env"]  # 获取当前数据库的环境类型
        if "user" in request.data:
            username = request.data["user"]
        else:
            username = request.user.get_username()
        if isinstance(request.data["excute_db_name"], list):
            database_name = request.data["excute_db_name"]
        else:
            database_name = eval(request.data["excute_db_name"])
        sql_data = request.data["operate_sql"]
        if ("select " in sql_data or "show " in sql_data) and len(database_name) > 1:
            return Response(status=400, data={"error": "不能同时查询多个数据库！"})
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
            if db_env:
                sql_info = obj.execute_sql(result, db_env=db_env)  # 非生产环境时，不进行脱敏
            else:
                sql_info = obj.desen(result)  # 生产环境时，进行脱敏操作
            if "FAIL" in sql_info[-1]["message"]:
                status = 0
                error_info = "失败sql：" + sql_info[-1]["sql"] + "\n" + sql_info[-1]["message"]
            data = {
                "env": base_data["environment"],
                "db_name": database_name_i,
                "operate_sql": sql_data,
                "performer": username,
                "status": status,
                "error_info": error_info,
                "sprint": sprint
            }
            # 将执行结果记录到日志
            OperateLogsView().create(data)
            if error_info:
                return Response(status=400, data={"error": sql_info})
        # return Response("恭喜你，全部sql执行成功！")
        return Response(data=sql_info)


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
        access_token = "241dc3a7aaf7c97ca10aa122f6e5568b1b0c6c3a4dbcc6454b08a64f0ca9d0c7"
        send_dingding_msg.delay(access_token, "text", "你有新的待审核的sql！")
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


re_params = openapi.Parameter('file_url', openapi.IN_QUERY, description="请求参数：导出路径，非必填，默认桌面", type=openapi.TYPE_STRING)
# 导出查询数据
@swagger_auto_schema(
    method='post',
    operation_summary='导出查询数据',
    manual_parameters=[re_params],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "data": openapi.Schema(title="此请求体用查询的响应data，格式为{'data': data}", type=openapi.TYPE_STRING),
        }
    ),
    responses={200: "ok"}
)
@require_POST
@csrf_exempt
@api_view(["POST"])
def export_excel(request):
    """
    post:
    导出查询数据；

    请求params：?file_url= ，不传时，导出到桌面
    请求体：{"data": 数据库执行接口返回的data或errors中的内容}
    """
    file_url = request.GET.get("file_url")
    file_data = json.loads(request.body).get("data")
    if not isinstance(file_data, list):
        return HttpResponse("文件数据格式为[{'data': [{}, {}]},]!")
    wb = Workbook()
    for file_data_i in file_data:
        if "data" in file_data_i and file_data_i["sql"].lower().startswith("select"):
            table_name = re.match(r'.* from (.*?)[\s|;]', file_data_i["sql"], re.I).group(1)
            ws = wb.create_sheet(table_name)
            for data_i in range(len(file_data_i["data"][0].keys())):
                ws.cell(row=1, column=data_i+1, value=list(file_data_i["data"][0].keys())[data_i])
            for data_i in range(len(file_data_i["data"])):
                for data_i_i in range(len(file_data_i["data"][data_i].values())):
                    ws.cell(row=data_i+2, column=data_i_i+1, value=list(file_data_i["data"][data_i].values())[data_i_i])
    if len(wb.sheetnames) > 1:
        del wb["Sheet"]
    if not file_url:
        # 如果没有给路径，直接导出到页面
        file_url = os.path.join(os.path.expanduser("~"), "Desktop")
    wb.save("%s/result.xlsx" % file_url)
    return HttpResponse("OK")
