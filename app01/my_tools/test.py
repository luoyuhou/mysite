#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/2
# Time:     20:54
# IDE :     PyCharm

import datetime
import time
import random
import hashlib
import re

# print(datetime.datetime('now'))

print('employ list len', len([]))
print('employ set len', len(set()))

dic = {'age': 20, 'name': 'jack'}

print('dic', list(dic))

s = set()
print(len(s))

print(time.time(), type(str(time.time())))
print(random.random(), str(random.random()))

print(hashlib.md5('123456'.encode()).hexdigest(), len(hashlib.md5('123456'.encode()).hexdigest()))
print(hashlib.sha256('123456'.encode()).hexdigest(), len(hashlib.sha256('123456'.encode()).hexdigest()))
print(hashlib.sha256('123456'.encode()).hexdigest(), len(hashlib.sha256('123456'.encode()).hexdigest()))

s = '/home/www/admin.txt'

s_path = s.split('/')
s_path[-1] = 'file-' + s_path[-1]
print('/'.join(s_path))

d = {'age': 29, 'name': 'jack'}
l = list(d)
print(l)
print([d], type([d]))


def myPrint(*args, **kwargs):
    print('args', args)
    print('kwargs', kwargs)


def theadDB(func=None, *args, **kwargs):
    if func is not None:
        func(args, kwargs)


theadDB(myPrint, 1, [1, 2], {'age': 20, 'name': 'jack'}, uid=12, group='jazz')
# args ((1, [1, 2], {'age': 20, 'name': 'jack'}), {'uid': 12, 'group': 'jazz'})
# kwargs {}
