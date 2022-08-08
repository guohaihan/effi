from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from dbms.engines.operateLogs import operateLogs
from dbms.models import OperateLogs, DBServerConfig, Audits, CheckContent
from rest_framework.response import Response
from django_filters.rest_framework.filterset import FilterSet
from django_filters import filters
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from dbms.serializers.operates import OperateLogsSerializer
from django_filters.rest_framework import DjangoFilterBackend
from dbms.engines.goInception import GoInceptionEngine
from rest_framework.filters import SearchFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from dbms.serializers.audits import AuditsSerializer
from drf_admin.utils.views import AdminViewSet
from rest_framework import status
from celery_tasks.dingding.tasks import send_dingding_msg
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from openpyxl import Workbook
from dbms.engines.mysql import MysqlEngine
import os, json, re
from django_redis import get_redis_connection


@require_POST
@csrf_exempt
@api_view(["POST"])
def check(request):
    """
    post:
    检查提交sql；

    请求体：
    {db: 数据库id,
    execute_db_name:执行数据名
    operate_sql：sql语句}
    """
    if "db" not in request.data or "execute_db_name" not in request.data or "operate_sql" not in request.data:
        return Response(status=400, data={"error": "请求参数缺失！"})
    if not request.data["db"] or not request.data["execute_db_name"] or not request.data["operate_sql"]:
        return Response(status=400, data={"error": "参数不能为空！"})
    db = request.data.get("db")
    # db_name是list，检查时，检查一个库即可
    db_name = request.data.get("execute_db_name")[0]
    sql = request.data.get("operate_sql")
    # 调用goInception中检查方法
    result = GoInceptionEngine.check(db, db_name, sql)
    if "error" in result:
        return Response(status=400, data={"error": result["error"]})
    # 将检查结果放入数据库
    if result["errorCount"] > 0:
        CheckContent.objects.create(sql_content=sql, status=0)
    else:
        CheckContent.objects.create(sql_content=sql, status=1)
    return Response(result)


class DatabasesView(APIView):
    """
    get:
    数据库操作--连接数据库

    获取信息详情, status: 201(成功), return: 数据库表
    post:
    数据库操作--执行sql

    获取信息详情, status: 201(成功), return: 执行结果
    """
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
        """获取所有数据库"""
        obj = MysqlEngine(pk)
        # 获取某个环境的数据
        all_db_list = obj.get_all_db()
        if isinstance(all_db_list, dict):
            return Response(status=400, data={"error": all_db_list["error"]})
        if request.query_params:
            # tenant用来过滤租户库
            if "tenant" not in request.query_params:
                return Response(status=400, data={"error": "请求参数为tenant"})
            for all_db_i in all_db_list[:]:
                if not all_db_i["Database"].startswith("guozhi_tenant_") or all_db_i["Database"] == "guozhi_tenant_1":
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
        """执行sql，并记录到日志"""
        if "db" not in request.data or "execute_db_name" not in request.data or "operate_sql" not in request.data:
            return Response(status=400, data={"error": "请求参数缺失！"})
        if not request.data["db"] or not request.data["execute_db_name"] or not request.data["operate_sql"]:
            return Response(status=400, data={"error": "参数不能为空！"})
        db = request.data["db"]
        db_names = request.data["execute_db_name"]
        sql = request.data["operate_sql"]
        obj = MysqlEngine(db)
        # 获取对应数据库连接信息
        base_data = obj.basic_info()
        if "error" in base_data:
            return Response(status=400, data={"error": base_data["error"]})
        # 获取当前数据库的环境类型
        db_env = DBServerConfig.objects.filter(id=db).values()[0]["db_env"]
        check_status = CheckContent.objects.filter(sql_content=sql, status=1).values()
        if db_env == 0 and check_status:
            return Response(status=400, data={"error": "生产数据库需审核后执行"})

        # 循环调用goInception中执行方法，操作多个数据库
        for db_name in db_names:
            result = GoInceptionEngine.execute(db, db_name, sql)
            result["db_env"] = base_data["environment"]
            result["db_name"] = db_name
            result["performer"] = request.user.get_username()
            result["sql"] = sql
            if "error" in result:
                return Response(status=400, data={"error": result["error"]})
            # 将检查结果放入数据库
            if result["errorCount"] > 0:
                result["status"] = 0
                for data in result["rows"]:
                    # goInception中0代表成功，1代表warn，2代表error
                    if data["error_level"] == 2:
                        result["error_message"] = data["error_message"]
                        break
                # 存入日志
                operateLogs(result)
                # 将goInception结果保存
                CheckContent.objects.create(sql_content=sql, status=0)
                return Response(status=400, data={"error": "执行失败，异常原因：%s" % result["error_message"]})
            else:
                CheckContent.objects.create(sql_content=sql, status=1)
            # 存入操作日志
            operateLogs(result)
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
        if "execute_db_name" in request.data:
            request.data["execute_db_name"] = json.dumps(request.data["execute_db_name"])
        user = request.user.get_username()
        request.data["user"] = user
        # 检查sql是否验证通过
        result = CheckContent.objects.filter(sql_content=request.data["operate_sql"], status=1).values()
        if not result:
            return Response(status=400, data={"error": "没有验证通过的语句不可以提交审核！"})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        access_token = "241dc3a7aaf7c97ca10aa122f6e5568b1b0c6c3a4dbcc6454b08a64f0ca9d0c7"
        send_dingding_msg.delay(access_token, "link", {
            "messageUrl": f"http://{request.META['HTTP_HOST']}/api/dbms/audits/?page=1&size=10&status=0",
            "picUrl": "https://img0.baidu.com/it/u=3821549314,1624213915&fm=253&fmt=auto&app=138&f=JPEG?w=773&h=500",
            "title": "SQL审核",
            "text": "这是上线需要审核的sql"
        })
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def multiple_update(self, request, *args, **kwargs):
    #     auditor = request.user.get_username()
    #     request.data["auditor"] = auditor
    #     return super().multiple_update(request, *args, **kwargs)

    def update(self, request, pk=None, *args, **kwargs):
        auditor = request.user.get_username()
        request.data["auditor"] = auditor
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 根据审核状态发送钉钉消息
        if request.data["status"] == "1":
            access_token = "241dc3a7aaf7c97ca10aa122f6e5568b1b0c6c3a4dbcc6454b08a64f0ca9d0c7"
            send_dingding_msg.delay(access_token, "text", "sql已审核通过，请观察操作日志，是否执行成功！")
        elif request.data["status"] == "2":
            access_token = "241dc3a7aaf7c97ca10aa122f6e5568b1b0c6c3a4dbcc6454b08a64f0ca9d0c7"
            send_dingding_msg.delay(access_token, "text", f"sql被驳回，驳回原因：{request.data['reason']}！")
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
