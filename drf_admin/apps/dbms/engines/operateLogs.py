# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : operateLogs.py
@create   : 2022/8/4 18:09
"""
from dbms.models import OperateLogs


def operateLogs(result):
    """处理操作日志数据"""
    status = 1
    error_info = None
    if "status" in result:
        status = result["status"]
        error_info = result["error_message"]
    data = {
        "env": result["db_env"],
        "db_name": result["db_name"],
        "operate_sql": result["sql"],
        "performer": result["performer"],
        "status": status,
        "error_info": error_info,
        "sprint": result["sprint"]
    }
    OperateLogs.objects.create(**data)
