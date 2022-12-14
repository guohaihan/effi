from dbms.models import DBServerConfig
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, RetrieveAPIView
from dbms.serializers.dbs import DBServerConfigSerializer
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from rest_framework.filters import SearchFilter
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
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('db_name','db_ip')

    def post(self, request, *args, **kwargs):
        username = request.user.get_username()
        request.data["create_user"] = username
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


