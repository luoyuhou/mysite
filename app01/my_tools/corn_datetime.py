#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/4
# Time:     13:55
# IDE :     PyCharm

import time
import datetime


# 当前时间戳转日期时间格式(秒单位)
def get_format_datetime(format_str='%Y-%m-%d %H:%M:%S', timestamp=0):
    if timestamp == 0:
        timestamp = int(time.time())
    return time.strftime(format_str, time.localtime(timestamp))


def get_format_millisecond_datetime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


def get_millisecond():
    return int(round(time.time() * 1000))


def get_second():
    return int(time.time())


def get_timestamp(datetime_str='', format_str=''):
    if datetime_str == '':
        return int(time.time())
    else:
        timeArray = time.strptime(datetime_str, format_str)
        return int(time.mktime(timeArray))


def get_datetime_difference(format_str1, format_str2=None):
    if format_str2 is None:
        timestamp2 = get_second()
    else:
        timestamp2 = get_timestamp(format_str2, '%Y-%m-%d %H:%M:%S')
    timestamp1 = get_timestamp(format_str1, '%Y-%m-%d %H:%M:%S')
    return get_timestamp_difference(timestamp1, timestamp2)


def get_timestamp_difference(timestamp1, timestamp2=None):
    if timestamp2 is None:
        timestamp2 = get_second()
    diff = timestamp1 - timestamp2
    return _timestamp_difference(diff)


def _timestamp_difference(diff=0):
    suffix = '后' if diff > 0 else '前'
    diff = abs(diff)
    if diff >= 31536000:  # 365 * 24 * 3600
        # 年
        ret_str = str(diff // 31536000) + '年' + suffix
    elif diff >= 86400:  # 24 * 3600
        # 天
        ret_str = str(diff // 86400) + '天' + suffix
    elif diff >= 3600:
        # 小时
        ret_str = str(diff // 3600) + '小时' + suffix
    elif diff >= 60:
        # 分钟
        ret_str = str(diff // 60) + '分钟' + suffix
    else:
        ret_str = '刚刚'
    return ret_str


if __name__ == "__main__":
    print('get_format_datetime', get_format_datetime())
    print('get_format_millisecond_datetime', get_format_millisecond_datetime())
    print('get_timestamp', get_timestamp(get_format_datetime(), '%Y-%m-%d %H:%M:%S'))
    print('millisecond', get_millisecond())
    print('difference', get_datetime_difference('2020-07-15 12:48:12'))
    print(get_timestamp())

