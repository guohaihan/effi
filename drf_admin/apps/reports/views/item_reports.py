# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : item_reports.py
@create   : 2021/12/2 13:43
"""
from datetime import datetime
from django.db import transaction
from django.db.models import Count, Avg, DecimalField, Sum
from rest_framework.decorators import action
from reports.models import ItemReports, Score, Story, JiraVersion
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from reports.serializers.item_reports import ItemReportsSerializer
from drf_admin.utils.views import AdminViewSet
from rest_framework import status
from django.db.models.functions import TruncMonth, TruncYear, TruncQuarter, Cast, Round
from jira import JIRA
from django.http import JsonResponse, HttpResponse
from dateutil.relativedelta import *
from django.db.models import F


def score(data):
    product_date = 0
    rf_date = 0
    todo_count = 0
    total_story = 0
    score_data = []
    if not {"rf_day", "group", "stories", "bug_classes"}.issubset(data.keys()):
        return "研发工作日、研发组数、故事、bug分类为必传字段！"
    if not data["group"] or not data["stories"] or not data["bug_classes"] or not data["rf_day"]:
        return "研发工作日、研发组数、故事、bug分类不能为空！"
    if not isinstance(data["group"], int):
        return "研发组数必须为整数！"
    if not isinstance(data["rf_day"], (float, int)):
        return "研发工作日必须为数字！"
    for story in data["stories"]:
        if not {"assess_length", "product_delays", "develop_delays", "smoking_by"}.issubset(story.keys()):
            return "故事中缺少必填项！"
        if not isinstance(story["assess_length"], (float, int)) or not isinstance(story["product_delays"], (float, int)) or not isinstance(story["develop_delays"], (float, int)):
            return "时长必须为数字！"
        if not isinstance(story["smoking_by"], bool):
            return "冒烟是否通过必须使用true/false值！"
        product_date += story["product_delays"]  # 产品延期总时长
        rf_date += story["develop_delays"]  # 开发延期总时长
        if not story["smoking_by"]:
            todo_count += 1  # 冒烟不通过数量
        total_story += story["assess_length"]  # 总故事点
    if not total_story:
        return "评估时长不能为0"
    if not data["rf_day"]:
        return "研发工作日不能为0"
    for bug in data["bug_classes"]:
        if not {"total_bug"}.issubset(bug.keys()):
            return "bug分类中未填写bug总数！"
        if not isinstance(bug["total_bug"], int):
            return "bug数量必须为整数！"
        total_bug = bug["total_bug"]  # bug数量
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
    todo = round((len(data["stories"])-todo_count)*2/len(data["stories"]), 2)

    # 计算单位bug分值
    unit_bug_i = round(total_bug/total_story, 2)
    if unit_bug_i >= 10:
        unit_bug = 0
    elif unit_bug_i < 0:
        return "bug数量或故事点错误!"
    else:
        unit_bug = round((10 - int(unit_bug_i))*4/10, 2)

    # 计算每天完成故事点
    # finish_story_day = round(total_story/(data["rf_day"]*data["group"]), 2)
    finish_story_day = round(total_story/data["rf_day"], 2)

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
    get_reports:
    报告统计--feature迭代

    列表, status: 201(成功), return: 列表
    get_jira_version:
    报告统计--jira版本

    列表, status: 201(成功), return: 列表
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
    queryset = ItemReports.objects.order_by("-name")
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
        # 支持日期搜索
        if "startDate" in request.GET and "endDate" in request.GET:
            output_field = DecimalField(max_digits=10, decimal_places=2)
            queryset = ItemReports.objects.filter(end_time__gte=request.GET["startDate"], end_time__lt=request.GET["endDate"]).aggregate(rfDay=Cast(Avg("rf_day"), output_field), totalDay=Cast(Avg("total_day"), output_field), scoreProductScore=Cast(Avg("score__product_score"), output_field), scoreRfDelay=Cast(Avg("score__rf_delay"), output_field), scoreTodo=Cast(Avg("score__todo"), output_field), scoreUnitBug=Cast(Avg("score__unit_bug"), output_field), scoreTotal=Cast(Avg("score__total"), output_field), scoreFinishStoryDay=Cast(Avg("score__finish_story_day"), output_field), testDay=Cast(Avg("test_day"), output_field), acceptanceDay=Cast(Avg("acceptance_day"), output_field))
            queryset.update(ItemReports.objects.filter(end_time__gte=request.GET["startDate"],
                                                  end_time__lt=request.GET["endDate"]).aggregate(storyCount=Cast(Count("story")/Count("story__item_reports", distinct=True), output_field), storyAssessLength=Cast(Sum("story__assess_length")/Count("story__item_reports", distinct=True), output_field)))
            queryset = [queryset]
            for queryset_i in queryset:
                queryset_info = ItemReports.objects.filter(end_time__gte=request.GET["startDate"], end_time__lt=request.GET["endDate"]).values("name", "content", rfDay=F("rf_day"), totalDay=F("total_day"), scoreProductScore=F("score__product_score"), scoreRfDelay=F("score__rf_delay"), scoreTodo=F("score__todo"), scoreUnitBug=F("score__unit_bug"), scoreTotal=F("score__total"), scoreFinishStoryDay=F("score__finish_story_day"), testDay=F("test_day"), acceptanceDay=F("acceptance_day"), storyCount=Count("story"), storyAssessLength=Sum("story__assess_length")).order_by("-name")
                queryset_i["info"] = queryset_info
            return Response(data=queryset)

        elif "type" not in request.GET:
            return Response(data={"error": "缺少类型参数，请求参数格式：type: year/quarter/month/sprint或startDate=&endDate="}, status=400)
        if request.GET["type"] in ["year", "month", "quarter"]:
            if request.GET["type"] == "year":
                type = TruncYear("end_time")
                add_date = relativedelta(years=1)
            elif request.GET["type"] == "quarter":
                type = TruncQuarter("end_time")
                add_date = relativedelta(months=3)
            else:
                type = TruncMonth("end_time")
                add_date = relativedelta(months=1)

            output_field = DecimalField(max_digits=10, decimal_places=2)
            queryset = ItemReports.objects.annotate(types=type).values("types").annotate(rfDay=Cast(Avg("rf_day"), output_field), totalDay=Cast(Avg("total_day"), output_field), scoreProductScore=Cast(Avg("score__product_score"), output_field), scoreRfDelay=Cast(Avg("score__rf_delay"), output_field), scoreTodo=Cast(Avg("score__todo"), output_field), scoreUnitBug=Cast(Avg("score__unit_bug"), output_field), scoreTotal=Cast(Avg("score__total"), output_field), scoreFinishStoryDay=Cast(Avg("score__finish_story_day"), output_field), testDay=Cast(Avg("test_day"), output_field), acceptanceDay=Cast(Avg("acceptance_day"), output_field))
            for queryset_i in queryset:
                queryset_i.update(ItemReports.objects.filter(end_time__gte=queryset_i["types"], end_time__lt=queryset_i["types"] + add_date).aggregate(storyCount=Cast(Count("story")/Count("story__item_reports", distinct=True), output_field), storyAssessLength=Cast(Sum("story__assess_length")/Count("story__item_reports", distinct=True), output_field)))
                queryset_info = ItemReports.objects.filter(end_time__gte=queryset_i["types"], end_time__lt=queryset_i["types"] + add_date).values("name", "content", rfDay=F("rf_day"), totalDay=F("total_day"), scoreProductScore=F("score__product_score"), scoreRfDelay=F("score__rf_delay"), scoreTodo=F("score__todo"), scoreUnitBug=F("score__unit_bug"), scoreTotal=F("score__total"), scoreFinishStoryDay=F("score__finish_story_day"), testDay=F("test_day"), acceptanceDay=F("acceptance_day"), storyCount=Count("story"), storyAssessLength=Sum("story__assess_length")).order_by("-name")
                queryset_i["info"] = queryset_info
            return Response(data=queryset)
        elif request.GET["type"] == "sprint":
            queryset = ItemReports.objects.all().values("name", "content", rfDay=F("rf_day"), totalDay=F("total_day"), scoreProductScore=F("score__product_score"), scoreRfDelay=F("score__rf_delay"), scoreTodo=F("score__todo"), scoreUnitBug=F("score__unit_bug"), scoreTotal=F("score__total"), scoreFinishStoryDay=F("score__finish_story_day"), testDay=F("test_day"), acceptanceDay=F("acceptance_day"), storyCount=Count("story"), storyAssessLength=Sum("story__assess_length")).order_by("-name")
            return Response(data=queryset)

        else:
            return Response(data={"error": "只支持年、季度、月、迭代"}, status=400)

    @action(detail=False, methods=["get"])
    @transaction.atomic
    def get_jira_version(self, request):
        """
        1，先查询jira数据；
        2，清空JiraVersion数据；
        3，向JiraVersion插入数据；
        4，进行年、季、月、指定时间查询；
        """
        current_date = datetime.now().strftime('%Y-%m-%d')
        jira_version_data = JiraVersion.objects.filter(create_time__date=current_date)
        if not jira_version_data:
            # 清空数据
            JiraVersion.objects.all().delete()
            server = "http://project.guoguokeji.com"
            try:
                jira_client = JIRA(server=server, basic_auth=("guohaihan", "guo126"))
            except Exception as e:
                return HttpResponse("失败原因：%s" % e, status=400)

            jira_version = jira_client.project_versions("GZ")
            jira_version_list = []
            for jira_version_i in jira_version:
                if jira_version_i.released:
                    if not hasattr(jira_version_i, "name"):
                        jira_version_i.name = None
                    if not hasattr(jira_version_i, "description"):
                        jira_version_i.description = None
                    if not hasattr(jira_version_i, "releaseDate"):
                        jira_version_i.releaseDate = None
                    if not hasattr(jira_version_i, "startDate"):
                        jira_version_i.startDate = None
                    jira_version_list.append({"name": jira_version_i.name, "released": jira_version_i.released, "description": jira_version_i.description, "start_date": jira_version_i.startDate, "release_date": jira_version_i.releaseDate})
                    JiraVersion.objects.update_or_create(**jira_version_list[-1])

        # 支持日期搜索
        if "startDate" in request.GET and "endDate" in request.GET:
            queryset = JiraVersion.objects.filter(start_date__gte=request.GET["startDate"], start_date__lt=request.GET["endDate"]).aggregate(total=Count("id"))
            hotfix_queryset = JiraVersion.objects.filter(start_date__gte=request.GET["startDate"], start_date__lt=request.GET["endDate"], name__startswith="hotfix").count()
            cs_queryset = JiraVersion.objects.filter(start_date__gte=request.GET["startDate"], start_date__lt=request.GET["endDate"], name__startswith="cs").count()
            feature_queryset = JiraVersion.objects.filter(start_date__gte=request.GET["startDate"], start_date__lt=request.GET["endDate"], name__startswith="feature").count()
            tech_queryset = JiraVersion.objects.filter(start_date__gte=request.GET["startDate"], start_date__lt=request.GET["endDate"], name__startswith="tech").count()
            released_queryset = JiraVersion.objects.filter(start_date__gte=request.GET["startDate"], start_date__lt=request.GET["endDate"], released=1).count()
            queryset["hotfix_total"] = hotfix_queryset
            queryset["cs_total"] = cs_queryset
            queryset["feature_total"] = feature_queryset
            queryset["tech_total"] = tech_queryset
            queryset["released_total"] = released_queryset

            return Response(data=queryset)

        elif "type" not in request.GET:
            return Response(data={"error": "缺少类型参数，请求参数格式：type: year/quarter/month或startDate=&endDate="}, status=400)

        if request.GET["type"] in ["year", "month", "quarter"]:
            if request.GET["type"] == "year":
                type = TruncYear("start_date")
            elif request.GET["type"] == "quarter":
                type = TruncQuarter("start_date")
            else:
                type = TruncMonth("start_date")

            queryset = JiraVersion.objects.annotate(types=type).values("types").annotate(total=Count("id"))
            hotfix_queryset = queryset.annotate(hotfix_total=Count("id")).filter(name__startswith="hotfix")
            cs_queryset = queryset.annotate(cs_total=Count("id")).filter(name__startswith="cs")
            feature_queryset = queryset.annotate(feature_total=Count("id")).filter(name__startswith="feature")
            tech_queryset = queryset.annotate(tech_total=Count("id")).filter(name__startswith="tech")
            released_queryset = queryset.annotate(released_total=Count("id")).filter(released=1)

            for queryset_i in queryset:
                queryset_i["hotfix_total"] = 0
                queryset_i["cs_total"] = 0
                queryset_i["feature_total"] = 0
                queryset_i["tech_total"] = 0
                queryset_i["released_total"] = 0
                for hotfix_queryset_i in hotfix_queryset:
                    if queryset_i["types"] == hotfix_queryset_i["types"]:
                        queryset_i["hotfix_total"] = hotfix_queryset_i["hotfix_total"]
                for cs_queryset_i in cs_queryset:
                    if queryset_i["types"] == cs_queryset_i["types"]:
                        queryset_i["cs_total"] = cs_queryset_i["cs_total"]
                for feature_queryset_i in feature_queryset:
                    if queryset_i["types"] == feature_queryset_i["types"]:
                        queryset_i["feature_total"] = feature_queryset_i["feature_total"]
                for tech_queryset_i in tech_queryset:
                    if queryset_i["types"] == tech_queryset_i["types"]:
                        queryset_i["tech_total"] = tech_queryset_i["tech_total"]
                for released_queryset_i in released_queryset:
                    if queryset_i["types"] == released_queryset_i["types"]:
                        queryset_i["released_total"] = released_queryset_i["released_total"]
        return Response(data=queryset)
