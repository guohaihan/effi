# -*- coding: utf-8 -*-
"""
@author   : Guo Hai Han
@software : PyCharm
@file     : urls.py
@create   : 2021/10/8 18:53
"""

from django.urls import path
from reports.views import jiras, item_reports
from drf_admin.utils.routers import AdminRouter

router = AdminRouter()
router.register(r'item_reports', item_reports.ItemReportsViewSet, basename='item_reports')
urlpatterns = router.urls
urlpatterns += [
    path("jiras/counts/", jiras.counts),  # 获取bug各类型数量
]