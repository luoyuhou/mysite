#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/8
# Time:     10:51
# IDE :     PyCharm

import time
import threading
from app01.my_tools.corn_settings import THREAD


class MyThread(threading.Thread):
    """继承Thread类重写run方法创建新进程"""
    semaphore = threading.BoundedSemaphore(THREAD['connects'])

    def __init__(self, func, args):
        """

        :param func: run方法中要调用的函数名
        :param args: func函数所需的参数
        """
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        print('当前子线程: {}'.format(threading.current_thread().name))
        print('args', self.args)
        self.func(self.args)
        # 调用func函数
        # 因为这里的func函数其实是上述的main()函数，它需要2个参数；args传入的是个参数元组，拆解开来传入


if __name__ == '__main__':
    def fun(*args):
        time.sleep(10)
        print('It is ara test!', args)

    pools = []
    for i in range(20):
        # pools.append(MyThread(fun, str(i)))
        t = MyThread(fun, str(i))
        t.start()

    print('len ===', len(pools))

    # for t in pools:
    #     print('t==', t)
    #     t.start()
    #
    # for t in pools:
    #     t.join()

