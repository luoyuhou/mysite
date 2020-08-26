#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/9
# Time:     11:02
# IDE :     PyCharm

from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url
from app01 import consumers


from channels.auth import AuthMiddlewareStack
import app01.routing


application = ProtocolTypeRouter({
    # 'websocket': URLRouter([
    #     # websocket 相关路由
    #     url(r'^ws/', consumers.ChatConsumer)
    # ])
    'websocket': AuthMiddlewareStack(
        URLRouter(
            app01.routing.websocket_urlpatterns
        )
    )
})