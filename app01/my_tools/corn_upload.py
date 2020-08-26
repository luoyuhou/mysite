#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/2
# Time:     18:53
# IDE :     PyCharm

import os
import time


def corn_upload_image(file, paths, file_hash, flag=0):
    """
    flag = 1 表示 不更换名字，用文件类型进行分类
    flag = 0 则随机生成名字，根据日期进行分类
    """
    print(len(file), type(file), str(file))

    if file is None:
        return None

    paths = paths
    paths.append('upload')
    file_list = file.name.split('.')
    if len(file_list) == 1:
        return None

    if flag == 0:
        paths.append('dynamic')
        paths.append(time.strftime('%Y%m%d', time.localtime(int(time.time()))))
    else:
        paths.append('still')
        paths.append(file_list[-1])

    path = ''
    for file_dir in paths:
        path = os.path.join(path, file_dir)
        if not os.path.exists(path):
            os.mkdir(path)

    filename = file.name
    if flag == 0:
        filename = '' + str(file_hash) + '.' + file_list[-1]
    destination = open(os.path.join(path, filename), 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()
    ret_path = '/'
    for i in paths[1:]:
        ret_path = os.path.join(ret_path, i)

    return {'file_path': os.path.join(ret_path, filename),
            'size': len(file), 'type': file_list[-1], 'filename': filename}
