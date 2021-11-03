# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : desensitises.py
@create   : 2021/10/13 16:20
"""
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django_redis import get_redis_connection
from rest_framework.decorators import api_view


@csrf_exempt
@api_view(["GET", "POST", "DELETE"])
def config(request):
    """
    get:
    获取脱敏数据

    return：配置数据
    post:
    设置脱敏数据

    请求体：{"desensitises": [], "limit": 1000}
    return：设置成功
    delete:
    删除配置数据

    请求params：?desensitises=，不传params时，做清空操作
    return：删除成功
    """
    conn = get_redis_connection('desensitises_config')
    if request.method == "GET":
        data = {"desensitises": [], "limit": 1000}  # 未设置时，默认为1000
        # desensitises = conn.lrange("desensitises", 0, -1)
        desensitises = conn.smembers("desensitises")
        limit = conn.get("limit")
        if desensitises:
            for d_i in desensitises:
                data["desensitises"].append(d_i.decode("utf-8"))
        if limit:
            data["limit"] = int(limit.decode("utf-8"))
        return JsonResponse(data)

    elif request.method == "POST":
        data = request.POST
        if not data:
            return HttpResponse("请求体为空！")
        if "desensitises" in data and data["desensitises"]:
            conn.sadd("desensitises", data["desensitises"])

        if "limit" in data and data["limit"]:
            conn.set("limit", data["limit"])
        return HttpResponse("设置成功!")

    elif request.method == "DELETE":
        data = request.GET
        if "desensitises" in data and data["desensitises"]:
            conn.srem("desensitises", data["desensitises"])
        else:
            conn.delete("desensitises")
        return HttpResponse("删除成功!")