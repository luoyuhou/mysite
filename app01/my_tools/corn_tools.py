#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/10
# Time:     14:55
# IDE :     PyCharm

import random
import hashlib

# 秘钥， 不可修改，否则用户登录不上
PRIVATE = 'MmNnOo'


def create_salt(length=6):
    """生成盐"""
    salt = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    len_chars = len(chars) - 1
    for i in range(0, length):
        salt += chars[random.randint(0, len_chars)]
    return salt


def create_password(key, salt):
    """生成密码"""
    return hashlib.sha256((PRIVATE + str(key) + str(salt)).encode()).hexdigest()


def check_password(key, salt, has):
    """检测密码"""
    return create_password(key, salt) == has


def create_hash(key):
    """生成hash"""
    return hashlib.md5((hashlib.sha256(str(key).encode()).hexdigest()).encode()).hexdigest()


def check_hash(key, has):
    """检验hash"""
    return create_hash(key) == has


if __name__ == '__main__':
    # sal = create_salt()
    # password = '123456'
    # ha = create_password(password, sal)
    # print('ha ======', ha)
    # print('digest = ', hashlib.sha256((password + sal).encode()).hexdigest())
    # print(check_password(password, sal, ha))

    # ke = '123456'
    # print(create_hash(ke))
    print(check_hash('', ''))
