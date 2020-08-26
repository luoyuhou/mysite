#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/7
# Time:     15:17
# IDE :     PyCharm

# server.py

# 导入系统模块
import os
import sys
# IO多路复用模块
import select
# 导入网络编程（传输层）模块
import socket
import queue

# 设置模块
from app01.my_tools.corn_settings import *
# 设置语言
from app01.my_tools.corn_language import *


def main():
    # Create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(False)

    # Bind the socket to the port
    print(sys.stderr, 'starting up on %s port %s' % SOCKET_SERVER['addr'])
    server.bind(SOCKET_SERVER['addr'])

    # Listen for incoming connections
    server.listen(SOCKET_SERVER['limit'])

    # Sockets from which we expect to read
    inputs = [server]

    # Sockets to which we expect to write
    outputs = []

    message_queues = {}

    while inputs:

        # Wait for at least one of the sockets to be ready for processing
        print('\nwaiting for the next event')
        readable, writable, exceptional = select.select(inputs, outputs, inputs)
        # Handle inputs
        for s in readable:

            if s is server:
                # A "readable" server socket is ready to accept a connection
                connection, client_address = s.accept()
                print('new connection from', client_address)
                connection.setblocking(False)
                inputs.append(connection)

                # Give the connection a queue for data we want to send
                message_queues[connection] = queue.Queue()
            else:
                size = SOCKET_SERVER['buffer_size']
                print('size', size)
                data = s.recv(size)
                if data:
                    # A readable client socket has data
                    print(sys.stderr, 'received "%s" from %s' % (data, s.getpeername()))
                    message_queues[s].put(data)
                    # Add output channel for response
                    if s not in outputs:
                        outputs.append(s)
                else:
                    # Interpret empty result as closed connection
                    print('closing', client_address, 'after reading no data')
                    # Stop listening for input on the connection
                    if s in outputs:
                        outputs.remove(s)  # 既然客户端都断开了，我就不用再给它返回数据了，所以这时候如果这个客户端的连接对象还在outputs列表中，就把它删掉
                    inputs.remove(s)  # inputs中也删除掉
                    s.close()  # 把这个连接关闭掉

                    # Remove message queue
                    del message_queues[s]
        # Handle outputs
        for s in writable:
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                # No messages waiting so stop checking for writability.
                print('output queue for', s.getpeername(), 'is empty')
                outputs.remove(s)
            else:
                print('sending "%s" to %s' % (next_msg, s.getpeername()))
                s.send(next_msg)
                # print('queues', len(outputs))
                # for c in outputs:
                #     if c is not s:
                #         c.send(next_msg)
        # Handle "exceptional conditions"
        for s in exceptional:
            print('handling exceptional condition for', s.getpeername())
            # Stop listening for input on the connection
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()

            # Remove message queue
            del message_queues[s]


if __name__ == '__main__':
    main()
