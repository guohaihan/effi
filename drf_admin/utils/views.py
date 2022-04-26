""" 
@author   : Wang Meng
@github   : https://github.com/tianpangji 
@software : PyCharm 
@file     : sqlscript.py
@create   : 2020/7/1 22:37 
"""
from rest_framework import status, serializers
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from drf_admin.utils.swagger_schema import OperationIDAutoSchema
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class MultipleDestroyMixin:
    """
    自定义批量删除mixin
    """
    swagger_schema = OperationIDAutoSchema

    class MultipleDeleteSerializer(serializers.Serializer):
        ids = serializers.ListField(required=True, write_only=True)

    @swagger_auto_schema(request_body=MultipleDeleteSerializer)
    def multiple_delete(self, request, *args, **kwargs):
        delete_ids = request.data.get('ids')
        if not delete_ids:
            return Response(data={'error': '参数错误,ids为必传参数'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(delete_ids, list):
            return Response(data={'error': 'ids格式错误,必须为List'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        del_queryset = queryset.filter(id__in=delete_ids)
        if len(delete_ids) != del_queryset.count():
            return Response(data={'error': '删除数据不存在'}, status=status.HTTP_400_BAD_REQUEST)
        del_queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MultipleUpdateMixin:
    """
    自定义批量更新mixin
    """
    swagger_schema = OperationIDAutoSchema

    class MultipleUpdateSerializer(serializers.Serializer):
        ids = serializers.ListField(required=True, write_only=True)

    @swagger_auto_schema(request_body=MultipleUpdateSerializer)
    def multiple_update(self, request, *args, **kwargs):
        update_ids = request.data.get('ids')
        if not update_ids:
            return Response(data={'error': '参数错误,ids为必传参数'}, status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(update_ids, list):
            return Response(data={'error': 'ids格式错误,必须为List'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = self.get_queryset()
        update_queryset = queryset.filter(id__in=update_ids)
        if len(update_ids) != update_queryset.count():
            return Response(data={'error': '更新数据不存在'}, status=status.HTTP_400_BAD_REQUEST)
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instances = []  # 这个变量是用于保存修改过后的对象，返回给前端
        for pk in update_ids:
            instance = get_object_or_404(update_queryset, id=pk)
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            instances.append(serializer.data)  # 将数据添加到列表中
        return Response(instances)


class AdminViewSet(ModelViewSet, MultipleDestroyMixin, MultipleUpdateMixin):
    """
    继承ModelViewSet, 并新增MultipleDestroyMixin, MultipleUpdateMixin
    添加multiple_delete action
    添加multiple_update action
    """
    pass


class TreeSerializer(serializers.ModelSerializer):
    """
    TreeAPIView使用的基类序列化器
    """
    id = serializers.IntegerField()
    label = serializers.CharField(max_length=20, source='name')
    pid = serializers.PrimaryKeyRelatedField(read_only=True)


class TreeAPIView(ListAPIView):
    """
    定义Element Tree树结构
    """

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        tree_dict = {}
        tree_data = []
        try:
            for item in serializer.data:
                tree_dict[item['id']] = item
            for i in tree_dict:
                if tree_dict[i]['pid']:
                    pid = tree_dict[i]['pid']
                    parent = tree_dict[pid]
                    parent.setdefault('children', []).append(tree_dict[i])
                else:
                    tree_data.append(tree_dict[i])
            results = tree_data
        except KeyError:
            results = serializer.data
        if page is not None:
            return self.get_paginated_response(results)
        return Response(results)


class ChoiceAPIView(APIView):
    """
    model choice字段API, 需指定choice属性或覆盖get_choice方法
    """
    choice = None

    def get(self, request):
        methods = [{'value': value[0], 'label': value[1]} for value in self.get_choice()]
        return Response(data={'results': methods})

    def get_choice(self):
        assert self.choice is not None, (
                "'%s' 应该包含一个`choice`属性,或覆盖`get_choice()`方法."
                % self.__class__.__name__
        )
        assert isinstance(self.choice, tuple) and len(self.choice) > 0, 'choice数据错误, 应为二维元组'
        for values in self.choice:
            assert isinstance(values, tuple) and len(values) == 2, 'choice数据错误, 应为二维元组'
        return self.choice


# 文件上传
@swagger_auto_schema(
    method='post',
    operation_summary='文件上传',
    type=openapi.IN_FORM,
    operation_description='Content-Type需要用这个:multipart/form-data',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "file": openapi.Schema(title="上传文件", type=openapi.TYPE_FILE)
        }
    ),
    responses={200: "返回文件内容"}
)
@csrf_exempt
@api_view(["post"])
def upload_file(request):
    """
    post:
    文件上传

    status: 200(成功), return: 文件内容
    """
    if request.method != 'POST':
        return HttpResponse('请求方法错误')
    f = request.FILES['file']
    if not f:
        return HttpResponse('获取上传文件错误')
    with open('drf_admin/media/files/%s' % f.name, 'w+', encoding="utf-8") as destination:
        for chunk in f.chunks():
            destination.write(chunk.decode())
    return HttpResponse(f.chunks())
