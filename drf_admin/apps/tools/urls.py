# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : urls.py
@create   : 2021/10/8 18:53
"""

from django.urls import path
from tools.views import jiras
from drf_admin.utils.routers import AdminRouter

router = AdminRouter()
urlpatterns = router.urls
urlpatterns += [
    path("jiras/counts/", jiras.counts),  # 获取bug各类型数量
]