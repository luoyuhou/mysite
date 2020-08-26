#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/7
# Time:     18:22
# IDE :     PyCharm

#######################
# socket 的配置
SOCKET_SERVER = {
    'host': '0.0.0.0',
    'port': 8090,
    'buffer_size': 1024,
    'limit': 10,
}
SOCKET_SERVER['addr'] = SOCKET_SERVER['host'], SOCKET_SERVER['port']

LANGUAGES = ['cn', 'en']
LANGUAGE = 'cn'


#######################
# 秘钥地址
PRIVATE_KEY = ''


#######################
# SSH 配置
OUT_TIME = 30


######################
# 多线程配置设置
THREAD = {
    'connects': 10
}


########################
# socket 实时聊天
CHAT = {
    'corpid': "",
    'secret': "",
    'sourceFile': "static/source",
    'serviceUser': 'serviceUser_',
    'customerUser': 'customerUser_',
    "media_image_url": "/static/uploadImage/",
    "avatar_image_url": "/static/images/",
    "avatar": "/static/images/system.png",
    'username': '系统通知',
    'type': 'group',
    'id': -1,
    'sign': '',
    'fromid': 0,
    'system': True,
    'title': '我的默默mua',
    'applyFriend': '申请添加你为好友',
    'agreeFriend': ' 同意了您的申请',
    'refuseFriend': ' 拒绝了您的申请',
}


####################
# session key
SESS_CONFIG = {
    'key': '_account_name',
    'expire': 30
}


#####################
# server
HTTP = {
    'port': 8080
}
