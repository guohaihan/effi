# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : tasks.py
@create   : 2021/9/23 01:20
"""
from celery_tasks.main import app
import requests, json, time
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


# 向钉钉群输出信息
@app.task(name="send_dingding_msg")
def send_dingding_msg(text):
    headers = {"Content-Type": "application/json;charset=utf-8"}
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=241dc3a7aaf7c97ca10aa122f6e5568b1b0c6c3a4dbcc6454b08a64f0ca9d0c7"
    data = {
        "msgtype": "text",
        "text": {"content": text}
    }
    try:
        response = requests.post(url=webhook, data=json.dumps(data), headers=headers)
        logger.info("钉钉消息发送成功：%s" % data["text"]["content"])
    except Exception as e:
        logger.error("钉钉消息发送失败：%s，失败原因:%s" % (data["text"]["content"], e))
