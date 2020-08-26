#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/7
# Time:     15:25
# IDE :     PyCharm


import datetime
import os

BASH_PATH = os.path.dirname(__file__)
LOGGER_FILE = 'error.log'


class Write(object):
    def __init__(self, filename=os.path.join(BASH_PATH, LOGGER_FILE), mode='a+', level='info'):
        self.model = mode
        self.filename = filename
        self.level = level.lower()
        # with open(os.path.join(BASH_PATH, filename), mode) as self.handler:
        #     pass
        self.handler = open(filename, mode)

    @classmethod
    def _datetime(cls):
        return '[' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') + ']'

    def info(self, message):
        if self.level == 'info':
            self.handler.write(Write._datetime() + ' [INFO] ' + str(message) + '\n')
            self._close()

    def debug(self, message):
        if self.level == 'debug' or self.level == 'warn' or self.level == 'error':
            self.handler.write(Write._datetime() + ' [DEBUG] ' + str(message) + '\n')
            self._close()

    def warn(self, message):
        if self.level == 'warn' or self.level == 'error':
            self.handler.write(Write._datetime() + ' [WARN] ' + str(message) + '\n')
            self._close()

    def error(self, message):
        self.handler.write(Write._datetime() + ' [ERROR] ' + str(message) + '\n')
        self._close()

    def _close(self):
        self.handler.close()


class Logger(Write):
    def __init__(self, level):
        super().__init__(level=level)
        Logger._instance = super()

    @classmethod
    def instance(cls, level='info'):
        if not hasattr(Logger, "_instance"):
            Logger._instance = Logger(level)

        return Logger._instance


if __name__ == '__main__':
    logger = Logger.instance(level='debug')
    logger.debug('1845151')
