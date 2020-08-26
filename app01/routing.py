#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/13
# Time:     16:18
# IDE :     PyCharm

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/app01/$', consumers.ChatConsumer),
]