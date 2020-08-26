#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/9
# Time:     11:04
# IDE :     PyCharm


from .models import *
from django.db.models import Q
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer, StopConsumer
from app01.my_tools.corn_settings import CHAT, SESS_CONFIG
from app01.my_tools.corn_datetime import get_millisecond, get_format_datetime
from app01.views import theadDB, sendMessage, addFriend, updateFriend, removeFriend, updateSendMessage
import json

channels = {}  # 用户的socket {'1': {id: 1, username: jack, socket: xxx}}
groups = {}  # 在线的讨论组成员 {'group_id': {'online': [], 'offline': []}}


def chat_output(dic, content='', msg_type=''):
    data = {
        'id': dic['id'],
        'username': dic['username'],
        'name': dic['username'],
        'sign': dic['sign'],
        'type': msg_type,
        'avatar': dic['avatar'],
        'content': content,
        'fromid': dic['id'],
        'timestamp': get_millisecond()
    }
    if hasattr(dic, 'system'):
        data['system'] = dic['system']
        data['type'] = dic['type']
    return data


def get_friend(user_id):
    """
    获取所有好友
    :param user_id:
    :return:
    """
    fids = Friend.objects.filter(Q(proposer=user_id, status=1) | Q(receiver=user_id, status=1)).all().values('id')
    fids = list(fids)
    data = []
    for fid in fids:
        data.append(fid['id'])
    return data


def get_online_friend(user_id):
    """
    获取玩家的在线好友
    :param user_id:
    :return:
    """
    fids = get_friend(user_id)
    data = []
    for fid in fids:
        if channels.get(fid, None) is not None:
            data.append({'id': fid, 'status': 'online'})
    return data


def get_offline_friend(user_id):
    """
    获取玩家的离线好友
    :param user_id:
    :return:
    """
    fids = get_friend(user_id)
    data = []
    for fid in fids:
        if channels.get(fid, None) is None:
            data.append({'id': fid, 'status': 'offline'})
    return data


def get_group(user_id):
    """
    查询该用户所在的讨论组
    :param user_id:
    :return:
    """
    gids = GroupAccount.objects.filter(user_id=user_id).values('group__id')
    print('gids', gids)
    data = []
    for item in gids:
        data.append(item['group__id'])
    return data


def get_group_account(group_id):
    """
    获取讨论组的所有成员
    :param group_id:
    :return:
    """
    uids = GroupAccount.objects.filter(id=group_id).all().values('user_id')
    uids = list(uids)
    print('user_ids', uids)
    data = []
    for item in uids:
        data.append(item['user_id'])
    return data


def set_group(user_id, gid, status):
    """
    将群聊添加到频道
    :param user_id:
    :param gid:
    :param status:
    :return:
    """
    g = groups.get(gid, None)
    # print('groups---', g, 'status', status, 'gid', gid)
    if g is None:
        group_account = get_group_account(gid)
        # print('group_account', group_account)
        if status == 'online':
            if user_id in group_account:
                group_account.remove(user_id)
            online_account = [user_id]
        else:
            online_account = []
        g = {'online': online_account, 'offline': group_account}
        groups[gid] = g
    else:
        if status == 'online':
            if user_id not in g['online']:
                g['online'].append(user_id)
            if user_id in g['offline']:
                g['offline'].remove(user_id)
        else:
            if user_id in g['online']:
                g['online'].remove(user_id)
            if user_id not in g['offline']:
                g['offline'].append(user_id)


def set_groups(user_id, status='online'):
    """
    设置群在线，用于玩家登录
    :param user_id:
    :param status:
    :return:
    """
    gids = get_group(user_id)
    for gid in gids:
        set_group(user_id, gid, status)


def get_user_online(uid):
    """
    判断玩家是否在线
    :param uid:
    :return:
    """
    if channels.get(uid, None) is not None:
        return True
    return False


def add_group_user(uids, gid):
    """
    添加玩家到群聊，用户创建群聊 或者 添加人员到群聊
    :param uids:
    :param gid:
    :return:
    """
    for uid in uids:
        # 判断玩家是否在线
        status = 'online' if get_user_online(uid) else 'offline'
        g = groups.get(gid, None)
        if g is not None:
            g = {'online': [], 'offline': []}
            g[status].append(uid)
            groups[gid] = g
        else:
            g[status].append(uid)


def remove_group_user(uids, gid):
    """
    移除玩家群聊
    :param uids:
    :param gid:
    :return:
    """
    g = groups.get(gid, None)
    if g is not None:
        for uid in uids:
            # 判断玩家是否在线
            status = 'online' if get_user_online(uid) else 'offline'
            g[status].remove(uid)


def send_group_message(gid, data, user_id=0):
    """
    发送消息
    :param user_id: user_id = 0 为系统消息
    :param gid:
    :param data:
    :return:
    """
    if user_id == 0:
        g = groups.get(gid, None)
        if g is not None:
            # 消息给离线者
            theadDB(sendMessage, user_id, g['offline'], data, gid)
            # 消息发送给在线者
            for uid in g['online']:
                if channels.get(uid, None) is not None:
                    channels[uid]['socket'].send(data)
    else:
        # 系统通知，如上下线通知
        for uid in channels:
            channels[uid]['socket'].send(data)


def friend_chat(params, user):
    tid = int(params['id'])
    data = chat_output(user, params['content'], 'friend')
    data = json.dumps({
            'type': 'chatMessage',
            'data': data
        })
    if channels.get(tid, None) is not None:
        channels[tid]['socket'].send(data)
    else:
        # 玩家离线
        theadDB(sendMessage, user['id'], [tid], data, 0)


def friend_add(params, user):
    print('friend_add', params)
    tid = int(params['id'])
    if channels.get(int(params['id']), None) is not None:
        channels[tid]['socket'].send(json.dumps({
                'type': 'sendMessage',
                'data': {
                    'username': user['username'],
                    'avatar': user['avatar'],
                    'id': user['id'],
                    'type': 'system',
                    'content': params['content']
                }
            }))
    theadDB(addFriend, user['id'], tid, int(params['group']), params['content'])


def friend_remove(params, user):
    content = user['username'] + ' 已经将您删除'
    tid = int(params['id'])
    if channels.get(tid, None) is not None:
        data = chat_output(CHAT, content)
        channels[tid]['socket'].send(json.dumps({
                'type': 'sendMessage',
                'data': data
            }))
    theadDB(removeFriend, user['id'], tid, content)


def friend_update(params, user):
    _type = 1 if params['type'] == 1 else 2
    tid = int(params['id'])
    msg = ' 已经同意好友申请' if _type == 1 else ' 拒绝了你的好友申请'
    content = user['username'] + msg
    if channels.get(tid, None) is not None:
        data = chat_output(CHAT, content)
        channels[tid]['socket'].send(json.dumps({
                'type': 'sendMessage',
                'data': data
            }))
    theadDB(updateFriend, user['id'], int(params['id']), _type, content)


def friend_status(params, user):
    uid = int(params['id'])
    content = 'online' if get_user_online(uid) is True else 'offline'
    data = chat_output(user, content)
    print('status', data)
    data['id'] = uid
    channels[user['id']]['socket'].send(json.dumps({
        'type': 'friendStatus',
        'data': data
    }))


def group_create():
    pass


def group_update():
    pass


def group_remove():
    pass


def group_chat(params, user):
    gid = int(params['id'])
    g = groups.get(gid)
    # print('g----', g)
    if g is not None:
        data = chat_output(user, params['content'], 'group')
        data['id'] = gid
        data = json.dumps({
            'type': 'chatMessage',
            'data': data
        })
        for uid1 in g['online']:
            if uid1 == user['id']:
                continue
            if channels.get(uid1, None) is not None:
                channels[uid1]['socket'].send(data)
        if len(g['offline']):
            theadDB(sendMessage, user['id'], g['offline'], data, gid)


def agree_friend(params, user):
    uid = int(params['id'])
    data = chat_output(user, '', params['type'])
    data['groupid'] = int(params['groupid'])
    print('agree_friend', data)
    if channels.get(uid, None) is not None:
        channels[uid]['socket'].send(json.dumps({
            'type': 'agreeFriend',
            'data': data
        }))


EventList = {
    'friend_chat': friend_chat,                         # 私聊
    'friend_add': friend_add,                           # 添加好友
    'friend_remove': friend_remove,                     # 删除好友
    'friend_update': friend_update,                     # 更新好友关系
    'friend_status': friend_status,                     # 查询好友状态
    'agree_friend': agree_friend,                       # 申请通过，通知对方
    'group_create': group_create,
    'group_update': group_update,
    'group_remove': group_remove,
    'group_chat': group_chat,
}


def chat_message(user):
    res = SendMessage.objects.filter(to_user_id=user['id'], is_read=0, msg__status=1).all().values('id', 'msg__msg')
    ids = []
    for msg in list(res):
        ids.append(msg['id'])
        user['socket'].send(msg['msg__msg'])
    if len(ids):
        theadDB(updateSendMessage, ids)


class ChatConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        print('有人进来了', message)  # 有人进来了 {'type': 'websocket.connect'}
        """客户端请求建立链接时 自动触发"""
        userInfo = json.loads(self.scope['session'][SESS_CONFIG['key']])
        self.accept()
        userInfo['socket'] = self
        user_id = userInfo['id']
        # 单点登录删除其他的登录
        chat_message(userInfo)
        for uid in channels:
            if uid == user_id:
                # 关闭连接
                pass
            else:
                # 通知其他上线
                data = chat_output(CHAT, userInfo['username'] + ' 上线了 ')
                channels[uid]['socket'].send(json.dumps({
                    'type': 'chatMessage',
                    'data': data
                }))
        channels[user_id] = userInfo
        # 设置群玩家在线、离线
        set_groups(userInfo['id'])

    def websocket_receive(self, message):
        """客户端发送数据过来  自动触发"""
        print('客户端发送的数据', type(message), message)
        # <class 'dict'> {'type': 'websocket.receive', 'text': '{"type":"connect","data":"connector with","id":1}'}
        userInfo = json.loads(self.scope['session'][SESS_CONFIG['key']])
        print('receive', userInfo)

        params = json.loads(message['text'])

        if params['type'] in EventList:
            print('data', type(params['data']), params['data'])
            EventList[params['type']](params['data'], userInfo)
        else:
            data = chat_output(CHAT, '未知消息 ')
            self.send(json.dumps({
                'type': 'chatMessage',
                'data': data
            }))

    def websocket_disconnect(self, message):
        """客户端断开链接之后  自动触发"""
        print('客户端断开连接', message)
        userInfo = json.loads(self.scope['session'][SESS_CONFIG['key']])
        print('disconnect', userInfo)

        for uid in list(channels.keys()):
            if uid == userInfo['id']:
                del channels[uid]
                set_groups(userInfo['id'], 'offline')
            else:
                # 通知其他人
                data = chat_output(CHAT, userInfo['username'] + ' 已掉线 ')
                channels[uid]['socket'].send(json.dumps({
                    'type': 'chatMessage',
                    'data': data
                }))

        raise StopConsumer()
