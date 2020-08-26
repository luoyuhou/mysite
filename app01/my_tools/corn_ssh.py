#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/7
# Time:     14:44
# IDE :     PyCharm


import paramiko
import threading
import os
from app01.my_tools.corn_settings import PRIVATE_KEY
from app01.my_tools.corn_logger import Logger


class ParamThreading(threading.Thread):
    def __init__(self, sid=0, host='192.168.238.131', servername='', port=22, username='root', password='123456', skey=0, params=None):
        super(ParamThreading, self).__init__()
        self._SSH = paramiko.SSHClient()
        self._transport = None
        self._SFTP = None
        self._SHH = None
        self.sid = sid
        self.host = host
        self.port = port
        self.servername = servername
        self.username = username
        self.password = password
        self.skey = skey
        self.params = params
        self._result = 0

    def run(self):
        self.connect()  # 连接远程服务器

    def connect(self):
        try:
            transport = paramiko.Transport((self.host, self.port))
            if self.skey == 1:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.load_system_host_keys()
                privatekey = os.path.expanduser(PRIVATE_KEY)
                key = paramiko.RSAKey.from_private_key_file(privatekey)
                transport.connect(username=self.username, password=self.password, pkey=key)
            else:
                transport.connect(username=self.username, password=self.password)
            self._transport = transport
            self._SFTP = paramiko.SFTPClient.from_transport(self._transport)
            self._SHH = paramiko.SSHClient()
            self._SHH._transport = self._transport

            print(self.params)
            if self.params.get('type') == 'cmd':
                self.cmd(self.params.get('cmd'))
            elif self.params.get('type') == 'upload':
                self.upload(self.params.get('local'), self.params.get('remote'))
            elif self.params.get('type') == 'download':
                self.download(self.params.get('local'), self.params.get('remote'))

        except Exception as e:
            Logger.instance().error(__file__ + str(e))
            exit(1)

    # def connect(self):
    #     ssh = paramiko.SSHClient()
    #     # 创建一个ssh的白名单
    #     know_host = paramiko.AutoAddPolicy()
    #     # 加载创建的白名单
    #     ssh.set_missing_host_key_policy(know_host)
    #
    #     # 连接服务器
    #     if self.skey == 1:
    #         # 免密登录
    #         ssh.load_system_host_keys()
    #         privatekey = os.path.expanduser(PRIVATE_KEY)
    #         key = paramiko.RSAKey.from_private_key_file(privatekey)
    #         ssh.connect(hostname=self.host, username=self.username, pkey=key)
    #     else:
    #         ssh.connect(
    #             hostname=self.host,
    #             port=self.port,
    #             username=self.username,
    #             password=self.password
    #         )
    #
    #     stdin, stdout, stderr = ssh.exec_command(self.command)
    #     print("ip:%s,\ncommand:%s,\n" % (self.host, self.command))
    #     print('stdin', stdin)
    #     print('stdout', stdout.read().decode())
    #     print('stderr', stderr)
    #     ssh.close()
    # return stdout.read().decode()

    def upload(self, local, remote):
        self._result = self._SFTP.put(local, remote)
        self.close()

    def close(self):
        self._transport.close()

    def cmd(self, command):
        stdin, stdout, stderr = self._SHH.exec_command(command)
        res = stdout.read()
        # print('res', res)
        self._result = res
        self.close()

    def download(self, local, remote):
        self._result = self._SFTP.get(remote, local)
        self.close()

    def get_result(self):
        return self._result

    def get_servername(self):
        return self.host if self.servername == '' else self.servername

    def get_sid(self):
        return self.sid


if __name__ == '__main__':
    pool = [
        dict(host="192.168.238.131", username="root", password="123456"),
        dict(host="192.168.238.131", username="root", password="123456"),
        dict(host="192.168.238.131", username="root", password="123456"),
        dict(host="192.168.238.131", username="root", password="123456"),
        dict(host="192.168.238.131", username="root", password="123456"),
        dict(host="192.168.238.131", username="root", password="123456"),
        dict(host="192.168.238.131", username="root", password="123456"),
        dict(host="192.168.238.131", username="root", password="123456"),
    ]

    t_pool = []
    for ser in pool:
        t = ParamThreading(host=ser.get('host', 'localhost'),
                           username=ser.get('username', 'root'),
                           password=ser.get('password', '123456'),
                           params={'type': 'cmd', 'cmd': 'ls'},
                           # 或者 params = {'type': 'upload', 'local': 'xxx', 'remote': 'yyy'}
                           )
        t_pool.append(t)

    for t in t_pool:
        t.start()

    for t in t_pool:
        t.join()
