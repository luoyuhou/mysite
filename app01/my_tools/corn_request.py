#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/4
# Time:     13:29
# IDE :     PyCharm


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # 所以这里是真实的ip
    else:
        ip = request.META.get('REMOTE_ADDR')  # 这里获得代理ip
    return ip


def get_agent(request):
    return request.headers.get('User-Agent', '')


def get_accept(request):
    return request.headers.get('Accept', '')


def get_content_type(request):
    return request.headers.get('Content-Type', '')


def get_path(request):
    return request.path if request.path else ''
