# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : tasks.py
@create   : 2021/9/23 01:20
"""
from celery_tasks.main import app
import requests, json, time
import logging
import hmac
import hashlib
import base64
import urllib.parse


def add_sign(secret):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    return sign, timestamp


# 向钉钉群输出信息
@app.task(name="send_dingding_msg")
def send_dingding_msg(access_token, msgtype, text):
    access_token = access_token
    sign, timestamp = add_sign("SECb58feb269f361c831451a53ebb69f1db9b80656f2f1d1018a5167e8ac163994e")
    headers = {"Content-Type": "application/json;charset=utf-8"}
    webhook = "https://oapi.dingtalk.com/robot/send?access_token=%s&timestamp=%s&sign=%s" % (access_token, timestamp, sign)
    if msgtype == "text":  # 文本消息
        data = {
            "msgtype": msgtype,
            "text": {"content": text}  # 消息内容，500字以内
        }
    elif msgtype == "image":  # 图片信息
        data = {
            "msgtype": msgtype,
            "image": {
                "media_id": text  # 媒体文件mediaid。可以通过上传媒体文件接口获取。
            }
        }
    elif msgtype == "voice":  # 语音消息
        data = {
            "msgtype": msgtype,
            "voice": {
               "media_id": text["media_id"],  # 媒体文件ID。可以通过上传媒体文件接口获取。
               "duration": text["duration"]  # 正整数，小于60，表示音频时长。
            }
        }
    elif msgtype == "file":  # 文件信息
        data = {
            "msgtype": msgtype,
            "file": {
                "media_id": text  # 媒体文件mediaid。可以通过上传媒体文件接口获取。
            }
        }
    elif msgtype == "link":  # 链接消息
        data = {
            "msgtype": msgtype,
            "link": {
                "messageUrl": text["messageUrl"],  # 消息点击链接地址，当发送消息为小程序时支持小程序跳转链接。
                "picUrl": text["picUrl"],  # 图片地址，可以通过上传媒体文件接口获取。
                "title": text["title"],  # 消息标题，建议100字符以内。
                "text": text["text"]  # 消息描述，建议500字符以内。
            }
        }
    elif msgtype == "oa":  # oa消息
        data = {
             "msgtype": msgtype,
             "oa": {
                "message_url": text["message_url"],  # 消息点击链接地址，当发送消息为小程序时支持小程序跳转链接。
                "head": text["head"],  # 消息头内容
                "body": text["body"]  # 消息体内容
            }
        }
    elif msgtype == "markdown":  # markdown消息
        data = {
            "msgtype": msgtype,
            "markdown": {
                "title": text["title"],  # 标题
                "text": text["text"]  # 内容
            }
        }
    elif msgtype == "actionCard":  # 卡片消息
        data = {
            "msgtype": msgtype,
            "actionCard": text
        }
    else:
        data = {
            "msgtype": "text",
            "text": {"content": "请求类型错误"}  # 消息内容，500字以内
        }
    try:
        response = requests.post(url=webhook, data=json.dumps(data), headers=headers)
        if response.status_code.startswith("2"):
            logging.getLogger("info").info("钉钉消息发送成功：%s" % data["text"]["content"])
        else:
            logging.getLogger("error").error("钉钉消息发送失败：%s，失败原因:%s" % (data["text"]["content"], response.content))
    except Exception as e:
        logging.getLogger("error").error("钉钉消息发送失败：%s，失败原因:%s" % (data["text"]["content"], e))
