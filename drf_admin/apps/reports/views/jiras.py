# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : jiras.py
@create   : 2021/10/8 16:35
"""
from jira import JIRA
from django.http import JsonResponse, HttpResponse
import re
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(method='get',
                     operation_summary='获取jira统计数',
                     manual_parameters=[openapi.Parameter('sprint', openapi.IN_QUERY, type=openapi.TYPE_STRING, description="版本号")],
                     responses={200: '统计数量'})
@api_view(["GET"])
def counts(request):
    """
    get:
    获取jira统计数

    请求params：?sprint= ，sprint（代表版本号）
    return:统计数
    """
    if request.method != "GET":
        return HttpResponse("只接受GET请求！", status=405)
    sprint = request.GET.get("sprint")
    if not sprint:
        return HttpResponse("sprint必填，格式?sprint=", status=400)
    server = "http://project.guoguokeji.com"
    try:
        jira_client = JIRA(server=server, basic_auth=("guohaihan", "guo126"))
    except Exception as e:
        return HttpResponse("失败原因：%s" % e, status=400)
    jql = """project = GZ AND status in (Open, "In Progress", Reopened, Resolved, 已关闭) AND fixVersion = "%s" ORDER BY assignee ASC, key DESC, summary ASC, created DESC""" % sprint
    story_jql = """project = GZ AND issuetype = 故事 AND fixVersion = "%s" ORDER BY summary DESC, key DESC, assignee ASC, created DESC""" % sprint
    try:
        issue_list = jira_client.search_issues(jql, maxResults=False)
        story_issue_list = jira_client.search_issues(story_jql, maxResults=False)
    except Exception as e:
        return HttpResponse(e.text, status=400)
    assignee_list = []
    issuetype_list = []
    story_list = []
    my_dict = {"assignee": assignee_list, "issuetype": issuetype_list, "story": story_list}
    for issue_i in issue_list:
        field = jira_client.issue(issue_i.key).fields
        assignee_list.append(str(field.assignee))  # assignee经办人
        issuetype_list.append(str(field.issuetype))  # issuetype问题类型

    for key in ["assignee", "issuetype"]:
        count = {}
        for li in my_dict[key]:
            count.setdefault(li, 0)
            count[li] += 1
        my_dict[key] = count

    for story_i in story_issue_list:
        story_field = jira_client.issue(story_i.key).fields
        # 获取研发人员
        rd_fe_list = story_field.customfield_10306
        rd_fe = []
        if rd_fe_list:
            for rd_fe_i in rd_fe_list:
                rd_fe.append(str(rd_fe_i))
        my_dict["story"].append({"key": story_i.key, "summary": story_field.summary, "story_point": story_field.customfield_10106, "rd_fe": rd_fe})

    return JsonResponse(my_dict)
