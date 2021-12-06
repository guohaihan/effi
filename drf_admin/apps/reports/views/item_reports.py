# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : item_reports.py
@create   : 2021/12/2 13:43
"""
from django.db.models import Count, Sum, Avg
from rest_framework.decorators import action
from reports.models import ItemReports, Score
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from reports.serializers.item_reports import ItemReportsSerializer
from drf_admin.utils.views import AdminViewSet
from rest_framework import status
from django.db.models.functions import TruncMonth, TruncWeek, TruncYear, TruncDay, TruncQuarter, Round


def score(data):
    product_date = 0
    rf_date = 0
    todo_count = 0
    total_story = 0
    score_data = []
    if not {"rf_day", "group", "storys", "bug_classs"}.issubset(data.keys()):
        return "研发工作日、研发组数、故事、bug分类为必传字段！"
    if not data["group"] or not data["storys"] or not data["bug_classs"] or not data["rf_day"]:
        return "研发工作日、研发组数、故事、bug分类不能为空！"
    if not isinstance(data["group"], int):
        return "研发组数必须为整数！"
    if not isinstance(data["rf_day"], (float, int)):
        return "研发工作日必须为数字！"
    for story in data["storys"]:
        if not {"assess_length", "product_delays", "develop_delays", "smoking_by"}.issubset(story.keys()):
            return "故事中缺少必填项！"
        if not isinstance(story["assess_length"], (float, int)) or not isinstance(story["product_delays"], (float, int)) or not isinstance(story["develop_delays"], (float, int)):
            return "时长必须为数字！"
        if story["smoking_by"] not in ["true", "false"]:
            return "冒烟是否通过必须使用true/false值！"
        product_date += story["product_delays"]  # 产品延期总时长
        rf_date += story["develop_delays"]  # 开发延期总时长
        if story["smoking_by"] == "false":
            todo_count += 1  # 冒烟不通过数量
        total_story += story["assess_length"]  # 总故事点
    for bug in data["bug_classs"]:
        if not {"rd", "fe"}.issubset(bug.keys()):
            return "bug分类中未填写前后端数量！"
        if not isinstance(bug["rd"], int) or not isinstance(bug["fe"], int):
            return "bug数量必须为整数！"
        total_bug = bug["rd"] + bug["fe"]  # bug数量
    # 计算pm改动需求分值
    if product_date > 3:
        product_score = 0
    elif product_date < 0:
        return "产品延期时长不合法"
    else:
        product_score = round((10-product_date*2)*3/10, 2)

    # 计算研发提测延期分值
    if rf_date > 3:
        rf_delay = 0
    elif rf_date < 0:
        return "产品延期时长不合法"
    else:
        rf_delay = round((10-rf_date*2)/10, 2)

    # 计算冒烟测试通过分值
    todo = round((len(data["storys"])-todo_count)*2/len(data["storys"]), 2)

    # 计算单位bug分值
    unit_bug_i = round(total_bug/total_story, 2)
    if unit_bug_i >= 10:
        unit_bug = 0
    elif unit_bug_i < 0:
        return "bug数量或故事点错误!"
    else:
        unit_bug = round((10 - int(unit_bug_i))*4/10, 2)

    # 计算每天完成故事点
    finish_story_day = round(total_story/(data["rf_day"]*data["group"]), 2)

    # 计算总分
    total = product_score + rf_delay + todo + unit_bug
    score_data.append({
        "product_score": product_score,  # pm改动需求导致延期得分
        "rf_delay": rf_delay,  # 研发故事延期
        "todo": todo,  # 冒烟通过率得分
        "unit_bug": unit_bug,  # 单位bug数
        "finish_story_day": finish_story_day,  # 每天完成故事点
        "total": "%0.2f" % total  # 迭代总分
    })
    return score_data


class ItemReportsViewSet(AdminViewSet):
    """
    list:
    报告--列表

    列表, status: 201(成功), return: 列表
    create:
    创建

    创建， status: 201(成功), return: 添加信息
    update:
    更新，支持局部

    进行更新操作, status: 201(成功), return: 更新后信息
    retrieve:
    详情信息

    信息, status: 201(成功), return: 数据信息
    multiple_update:
    批量更新，支持局部

    信息, status: 201(成功), return: 更新后数据信息
    multiple_delete:
    批量删除

    信息, status: 201(成功), return: null
    destroy:
    删除

    信息, status: 201(成功), return: null
    """
    queryset = ItemReports.objects.order_by("-update_time")
    serializer_class = ItemReportsSerializer
    # 自定义过滤字段
    filter_backends = [SearchFilter]
    search_fields = ("name", "content")

    def create(self, request, *args, **kwargs):
        score_data = score(request.data)
        if isinstance(score_data, str):
            return Response(data={"error": score_data}, status=400)
        request.data["scores"] = score_data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        score_data = score(request.data)
        if isinstance(score_data, str):
            return Response(data={"error": score_data}, status=400)
        request.data["scores"] = score_data
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def get_reports(self, request):
        if request.GET["type"] in ["year", "month", "quarter"]:
            if request.GET["type"] == "year":
                type = TruncYear("item_reports__end_time")
            elif request.GET["type"] == "quarter":
                type = TruncQuarter("item_reports__end_time")
            else:
                type = TruncMonth("item_reports__end_time")
            queryset = Score.objects.annotate(type=type).values("type").annotate(unit_bug=Avg("unit_bug"), total=Avg("total"), finish_story_day=Avg("finish_story_day"), todo=Avg("todo"), count=Count("id"))
            return Response(data=queryset)
        else:
            return Response(data={"error": "只支持年、季度、月"}, status=400)

