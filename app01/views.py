from captcha.helpers import captcha_image_url
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.db.models import Q
from django.views import View
from django.db import transaction
from .models import Account, Schedule, ScheduleProcess, Attachment, Article, Active, Blog, Command, Server, ServerGroup, \
    Group, FileTransfer, FriendGroup, GroupAccount, Message, SendMessage, Friend, Notice, FriendGroupFriend
import random
import json
import os
import time
import hashlib
from captcha.models import CaptchaStore

BASE_PATH = os.path.realpath(os.path.dirname(__file__))

from mysite.settings import BASE_DIR
from app01.my_tools import corn_datetime, corn_upload, corn_request, corn_ssh, corn_thread, corn_tools
from app01.my_tools.corn_logger import Logger
from app01.forms import LoginForm
from app01.my_tools.corn_settings import SESS_CONFIG, CHAT, HTTP

logger = Logger.instance()


# 验证用户是否登录
def check_login(fn):
    def wrapper(request, *args, **kwargs):
        print('session', request.session.get(SESS_CONFIG['key']))
        if request.session.get(SESS_CONFIG['key'], None):
            return fn(request, *args, *kwargs)
        return HttpResponseRedirect('/login/')

    return wrapper


# class index(LoginRequired):
#     model = Account
#     template_name = 'app01/index.html'


class Data(object):
    """用于返回数据格式"""
    code = 0
    msg = '操作成功'
    data = None
    count = 0


def format_output(obj):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not callable(value) and not name.startswith('_'):
            pr[name] = value
    # print('---------format', type(pr), pr)
    return JsonResponse(pr)


@check_login
def index(request):
    user = json.loads(request.session[SESS_CONFIG['key']])
    # print('id ===', user_id)
    return render(request, 'app01/index.html', {'chat': CHAT, 'http': HTTP})


def login(request):
    if request.session.get(SESS_CONFIG['key']):
        return HttpResponseRedirect('/')
    if request.is_ajax():
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        verify = request.POST.get('verify', '')
        hashkey = request.POST.get('captcha_0', '')

        if username is None or password is None or verify == '' or hashkey == '':
            return JsonResponse({
                'code': 100008,
                'msg': '参数错误',
                'data': [],
                'count': 0
            })
        else:
            if CaptchaStore.objects.filter(response=verify, hashkey=hashkey):
                print('login request', request.POST)
                username = username.strip()
                password = password.strip()
                user = Account.objects.filter(username=username, status=1).values('id', 'username', 'nickname',
                                                                                  'password', 'salt', 'avatar', 'sign',
                                                                                  'phone', 'state', 'manager',
                                                                                  'group_id_id')
                user = list(user)

                if len(user) != 0:
                    user = user[-1]
                    if corn_tools.check_password(password, user.get('salt'), user.get('password')):
                        request.session[SESS_CONFIG['key']] = json.dumps(user)
                        return JsonResponse({
                            'code': 0,
                            'msg': '登录成功',
                            'data': [],
                            'count': 0
                        })
                return JsonResponse({
                    'code': 100002,
                    'msg': '账号不存在或密码错误',
                    'data': [],
                    'count': 0
                })
                # return HttpResponseRedirect('/')
            else:
                return JsonResponse({
                    'code': 1000012,
                    'msg': '验证码错误',
                    'data': [],
                    'count': 0
                })
    else:
        login_form = LoginForm()
        return render(request, 'app01/login.html', {'login_form': login_form})


def article(request):
    return HttpResponse('layout article')


def home(request):
    if request.method == 'POST':
        page, limit = _where(request)
        count = Schedule.objects.filter().count()
        data = Schedule.objects.filter().all().order_by('deadline')[(page - 1) * limit: page * limit].values(
            'id', 'publisher__username', 'title', 'content', 'image_path', 'status', 'urgent', 'pub_date', 'deadline'
        )
        return JsonResponse({
            'code': 0,
            'msg': '',
            'data': list(data),
            'count': count
        })
    else:
        toolbar = [{'title': 'index', 'url': ''},
                   {'title': 'add', 'url': "/home/add"},
                   {'title': 'edit', 'url': "/auth/edit"},
                   {'title': 'del', 'url': "/auth/del"}]
        title = 'schedule'
        detail = '任务进度一览表'
        operate = [{'title': 'edit'}, {'title': 'del'}]
        print(request.POST, len(request.POST))
        return render(request, 'app01/home/index.html', locals())


def home_add(request):
    print(request.POST, len(request.POST))
    if len(request.POST):
        publisher = Account.objects.get(id=int(request.POST.get('publisher', 0)))
        title = request.POST.get('title')
        content = request.POST.get('content')
        image_path = request.POST.get('image_path', '')
        status = request.POST.get('status', 0)
        urgent = request.POST.get('urgent', 0)
        deadline = request.POST.get('deadline')
        pub_date = corn_datetime.get_format_datetime()
        print('----', publisher, title, content, deadline)
        if publisher is not None and content is not None and title is not None and deadline is not None:
            res = None
            try:
                res = Schedule.objects.create(publisher=publisher, title=title, content=content,
                                              image_path=image_path, status=status, urgent=urgent,
                                              pub_date=pub_date, deadline=deadline)
                print('add', res)

            except Exception as e:
                logger.error('home_add 错误' + str(e))
            finally:
                if res is not None:
                    return JsonResponse({
                        'code': 0,
                        'msg': '操作成功',
                        'data': [],
                        'count': 1
                    })
                else:
                    return JsonResponse({
                        'code': 100007,
                        'msg': '操作失败',
                        'data': [],
                        'count': 0
                    })
        else:
            return JsonResponse({
                'code': 100004,
                'msg': '参数有误',
                'data': [],
                'count': 0
            })
    else:
        title = '添加任务'
        detail = '安排任务'
        users = _selectAccount()
        print('list', users)
        form = [
            {
                'label': '发布者',
                'element': [
                    {'elem': 'select', 'type': '', 'name': 'publisher', 'verify': 'required', 'filter': '',
                     'value': users}]
            },
            {
                'label': '标题',
                'element': [
                    {'elem': 'input', 'type': 'text', 'name': 'title', 'verify': 'required', 'filter': '', 'value': [],
                     'placeholder': "请输入标题"}]
            },
            {
                'label': '描述',
                'element': [
                    {'elem': 'input', 'type': 'text', 'name': 'content', 'verify': 'required', 'filter': '',
                     'value': [],
                     'placeholder': "请输入描述"}]
            },
            {
                'label': '图片地址',
                'element': [{'elem': 'input', 'type': 'text', 'name': 'image_path', 'verify': '', 'filter': '',
                             'value': [],
                             'placeholder': "请上传图片"},
                            {
                                'elem': 'input',
                                'type': 'button',
                                'name': '',
                                'id': 'upload_img',
                                'filter': 'rule-add-search',
                                'value': {'title': '上传图片'}
                            }]
            },
            {
                'label': '任务状态',
                'element': [{'elem': 'input', 'type': 'radio', 'name': 'status', 'verify': '', 'filter': '',
                             'value': [{'title': '完成', 'val': 1, 'checked': 0},
                                       {'title': '未完成', 'val': 0, 'checked': 1}]}]
            },
            {
                'label': '是否紧急',
                'element': [{'elem': 'input', 'type': 'radio', 'name': 'urgent', 'verify': '', 'filter': '',
                             'value': [{'title': '紧急', 'val': 1, 'checked': 0},
                                       {'title': '非紧急', 'val': 0, 'checked': 1}]}]
            },
            {
                'label': '截止日期',
                'element': [
                    {'elem': 'input', 'type': 'datetime', 'name': 'deadline', 'verify': 'required', 'filter': '',
                     'value': []}]
            }
        ]
        return render(request, 'app01/home/add.html', locals())


def _selectAccount():
    data = Account.objects.filter().all().values('id', 'username')
    users = []
    if len(data) != 0:
        for user in data:
            user['name'] = user['username']
            users.append(user)
    return users


def _upload(request, flag):
    file = request.FILES.get('file', None)
    res = []
    if file is not None:
        print(file.name)
        if flag == 1:
            file_hash = hashlib.sha256(file.name.encode(encoding='UTF-8', errors='strict')).hexdigest()
            res = Attachment.objects.filter(hash=file_hash).values('file_path', 'filename')
            print('file_hash', file_hash)
            print('hash_path', res, type(res))
            res = list(res)
            print('item', res)
        else:
            file_hash = hashlib.sha256(str(time.time()) + str(random.random())).hexdigest()
        if len(res) == 0:
            res = corn_upload.corn_upload_image(file, [BASE_DIR, 'static'], file_hash, flag)
            print(res)
            if len(res) != 0:
                pub_date = corn_datetime.get_format_datetime()
                ip = corn_request.get_ip(request)
                Attachment.objects.create(filename=res['filename'], file_path=res['file_path'],
                                          size=res['size'], hash=file_hash, pub_date=pub_date, ip=ip)
                res = [res]
    return res


def upload_image(request):
    res = _upload(request, 0)
    if len(res) != 0:
        # print('eventually file_path', res)
        data = {
            'code': 0,
            'msg': '',
            'data': [res[-1]['file_path']],
            'count': 1
        }
    else:
        data = {
            'code': 100005,
            'msg': '上传失败',
            'data': [],
            'count': 0
        }
    return JsonResponse(data)


def upload_rimage(request):
    res = _upload(request, 1)
    if len(res) != 0:
        print('eventually file_path', res)
        data = {
            'code': 0,
            'msg': '上传成功',
            'data': [res[-1]['file_path']],
            'count': 1
        }
    else:
        data = {
            'code': 100005,
            'msg': '上传失败',
            'data': [],
            'count': 0
        }
    return JsonResponse(data)


def upload_image_lay(request):
    res = _upload(request, 0)
    print('----', res)
    if len(res) != 0:
        data = {
            'code': 0,
            'msg': '上传成功',
            'data': {'src': res[-1]['file_path'], 'title': res[-1]['filename']},
            'count': 1
        }
    else:
        data = {
            'code': 100005,
            'msg': '上传失败',
            'data': {},
            'count': 0
        }
    return JsonResponse(data)


def upload_multiple_image(request):
    return JsonResponse({
        'code': 100004,
        'msg': '参数有误',
        'data': [],
        'count': 0
    })


def attachment(request):
    if len(request.POST):
        page, limit = _where(request)
        count = Attachment.objects.count()
        data = Attachment.objects.all()[(page - 1) * limit: page * limit].values(
            'id', 'filename', 'size', 'file_path', 'ip', 'operator', 'pub_date'
        )
        return JsonResponse({
            'code': 0,
            'msg': '',
            'data': list(data),
            'count': count
        })
    else:
        title = 'attachment'
        detail = '附件表'
        toolbar = [{'title': 'index', 'url': ''},
                   {'title': 'add', 'url': "/home/add"},
                   {'title': 'edit', 'url': "/auth/edit"},
                   {'title': 'del', 'url': "/auth/del"}]
        operate = [{'title': 'edit'}, {'title': 'del'}]
        return render(request, 'app01/attachment/index.html', locals())


def active(request):
    if request.method == 'POST':
        content = request.POST.get('content', None)
        image_path = request.POST.get('image_path', '')
        account_id = 1
        operator = Account.objects.get(id=account_id)
        res = None
        if content is not None and operator is not None:
            pub_date = corn_datetime.get_format_datetime()
            ip = corn_request.get_ip(request)
            try:
                res = Active.objects.create(operator=operator, content=content, image_path=image_path,
                                            pub_date=pub_date, ip=ip)
            except Exception as e:
                logger('active ' + str(e))
            finally:
                if res is not None:
                    return JsonResponse({
                        'code': 0,
                        'msg': '操作成功',
                        'data': [],
                        'count': 1
                    })
                else:
                    return JsonResponse({
                        'code': 100007,
                        'msg': '操作失败',
                        'data': [],
                        'count': 0
                    })
    else:
        title = 'active'
        detail = '记录每一天'
        form_url = ''
        form_url_get = './get/'
        return render(request, 'app01/active/index.html', locals())


def active_get(request):
    if request.method == 'POST':
        a_id = int(request.POST.get('a_id', 0))
        page, limit = _where(request)
        print('a_id = ', a_id, 'limit = ', limit)
        if a_id == 0:
            data = Active.objects.filter().order_by('-pub_date')[0: limit].values('id', 'content',
                                                                                  'image_path',
                                                                                  'operator__username',
                                                                                  'pub_date')
        else:
            data = Active.objects.filter(id__lt=a_id).order_by('-pub_date')[0: limit].values('id', 'content',
                                                                                             'image_path',
                                                                                             'operator__username',
                                                                                             'pub_date')
        data = list(data)
        return JsonResponse({
            'code': 0,
            'msg': '已刷新',
            'data': data,
            'count': len(data)
        })
    else:
        return JsonResponse({
            'code': 100008,
            'msg': '请求失败',
            'data': [],
            'count': 0
        })


def blog(request):
    if request.method == 'POST':
        print(request.POST)
        page, limit = _where(request)
        count = Blog.objects.filter(public=1).count()
        print('page', page, 'limit', limit, 'count', count)
        data = Blog.objects.filter(public=1).all().order_by('-pub_date')[(page - 1) * limit: page * limit].values(
            'id', 'operator__username', 'title', 'content', 'public', 'pub_date')
        print('data', data)
        return JsonResponse({
            'code': 0,
            'msg': '',
            'data': list(data),
            'count': count
        })
    else:
        toolbar = [{'title': 'index', 'url': ''},
                   {'title': 'add', 'url': "/blog/add"}]
        title = 'blog'
        detail = '记录好文章'
        operate = [{'title': 'edit'}, {'title': 'del'}]
        table_url = './'
        print(request.POST, len(request.POST))
        return render(request, 'app01/blog/index.html', locals())


def blog_view(request, user_id):
    if request.method == 'POST':
        page, limit = _where(request)
        count = Blog.objects.filter(operator_id=user_id).count()
        data = Blog.objects.filter(operator_id=user_id).all().order_by('-pub_date')[
               (page - 1) * limit: page * limit].values(
            'id', 'operator__username', 'title', 'content', 'public', 'pub_date')
        return JsonResponse({
            'code': 0,
            'msg': '',
            'data': list(data),
            'count': count
        })
    else:
        toolbar = [{'title': 'index', 'url': ''},
                   {'title': 'add', 'url': "/blog/add"},
                   {'title': 'edit', 'url': "/blog/edit"},
                   {'title': 'del', 'url': "/blog/del"}]
        title = 'blog'
        detail = '记录好文章'
        operate = [{'title': 'edit'}, {'title': 'del'}]
        table_url = './'
        print(request.POST, len(request.POST))
        return render(request, 'app01/blog/index.html', locals())


def blog_edit(request):
    operator = 2
    blog_id = int(request.GET.get('id', 0))
    print(blog_id, type(blog_id))
    data = get_object_or_404(Blog, pk=blog_id)

    # only view
    upload_url = '../../upload/image_lay/'
    edition = 0
    if data.operator_id == operator:
        edition = 1
    return render(request, 'app01/blog/edit.html', locals())


def blog_add(request):
    if request.method == 'POST':
        print(request.POST)
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        public = request.POST.get('public', 1)
        pub_date = corn_datetime.get_format_datetime()
        operator = Account.objects.get(id=int(request.POST.get('publisher', 1)))
        if title == '' or content == '':
            return JsonResponse({
                'code': 100004,
                'msg': '参数有误',
                'data': [],
                'count': 1
            })
        else:
            res = None
            try:
                res = Blog.objects.create(title=title, content=content, public=public, operator=operator,
                                          pub_date=pub_date)
            except Exception as e:
                logger.error('blog_add ' + str(e))
            finally:
                if res is not None:
                    return JsonResponse({
                        'code': 0,
                        'msg': '操作成功',
                        'data': [],
                        'count': 1
                    })
                else:
                    return JsonResponse({
                        'code': 100007,
                        'msg': '操作失败',
                        'data': [],
                        'count': 0
                    })
    else:
        title = 'publish blog'
        detail = '写个人博客'
        upload_url = '../../upload/image_lay/'
        return render(request, 'app01/blog/add.html', locals())


def command(request):
    user_id = json.loads(request.session[SESS_CONFIG['key']]).get('id')
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        limit = int(request.POST.get('limit', 10))
        print('command', 'page = ', page, 'limit = ', limit)
        count = Command.objects.filter(operator_id=user_id).count()
        print('count', count)
        data = Command.objects.filter(operator_id=user_id).all().order_by('-start_date')[
               (page - 1) * limit: page * limit].values('id', 'ip__servername', 'cmd', 'content',
                                                        'operator__username', 'start_date', 'end_date')
        return JsonResponse({
            'code': 0,
            'msg': '',
            'data': list(data),
            'count': count
        })
    else:
        toolbar = [{'title': 'index', 'url': ''}, {'title': 'add', 'url': "/command/add"}]
        title = 'command'
        detail = '执行命令记录'
        operate = [{'title': 'detail'}]
        table_url = './'
        return render(request, 'app01/command/index.html', locals())


def command_add(request):
    if request.method == 'POST':
        ser = str(request.POST.get('server[]', '')).strip()
        group = str(request.POST.get('group[]', '')).strip()
        cmd = request.POST.get('cmd', '')
        operator = json.loads(request.session[SESS_CONFIG['key']]).get('id')
        if ser != '' and group != '' and cmd != '':
            # return JsonResponse(test(10))
            # t = corn_thread.MyThread(_command_add, (ser, group, operator, cmd))
            # t.start()
            data = _command_add((ser, group, operator, cmd))
            return JsonResponse(data)
        else:
            return JsonResponse({
                'code': 100008,
                'msg': '参数错误',
                'data': [],
                'count': 0
            })
    else:
        title = 'execute command'
        detail = '执行命令'
        operate = [{'title': 'detail'}]
        table_url = './'
        group = ServerGroup.objects.all().values('id', 'group_name')
        group = list(group)
        print('group', group)
        servers = Server.objects.all().values('id', 'servername')
        servers = list(servers)
        print('servers', servers)
        return render(request, 'app01/command/add.html', locals())


def _server(ser, user_id=0):
    ser_list = str(ser).strip().split(',')
    ser_list = list(map(int, ser_list))
    data = Server.objects.filter(id__in=ser_list, status=1).all().values('id', 'ip', 'servername', 'username',
                                                                         'password', 'skey', 'deny_user')
    return list(data)


def _command_add(args):
    """
    ser, group, operator, cmd
    ser, group, operator, int(cmd), local_path, remote_path
    :param args: args[0] = server, args[1] = group, args[2] = operator, args[3] = cmd, args[4] = local, args[5] = remote
    :return: dict
    """
    star_time = corn_datetime.get_format_millisecond_datetime()
    group_list = str(args[1]).strip().split(',')
    group_list = list(map(int, group_list))
    operator = args[2]
    cmd = args[3]
    ser_arr = _server(ser=args[0], user_id=operator)

    pools = []
    results = []
    ips = []
    size = 0  # 文件大小
    fail_server = []  # 传输失败的服务器
    for item in ser_arr:
        if cmd == 1:
            params = {'type': 'upload', 'local': args[4], 'remote': args[5]}
        elif cmd == 2:
            local = args[4].replace('\\', '/')
            local_path = local.split('/')
            local_path[-1] = item['servername'] + '-' + local_path[-1]
            params = {'type': 'download', 'local': '/'.join(local_path), 'remote': args[5]}
        else:
            params = {'type': 'cmd', 'cmd': cmd}
        t = corn_ssh.ParamThreading(sid=int(item['id']), host=item['ip'], username=item['username'],
                                    password=item['password'], skey=item['skey'], params=params)
        pools.append(t)
        ips.append(int(item['id']))
    for t in pools:
        t.start()

    for t in pools:
        t.join()
        res = t.get_result()
        if cmd == 1 or cmd == 2:
            if res == 0:
                fail_server.append(t.get_sid())
            else:
                results.append(t.get_servername())
                # print(res.__dict__)
                size = res.__dict__['st_size'] if res.__dict__['st_size'] >= size else size

        else:
            res = 'server connect fail' if res == 0 else res.decode()
            results.append(t.get_servername() + ' ==>\n' + res)

    end_time = corn_datetime.get_format_millisecond_datetime()

    # print('result', results)
    # print('ips', ips)
    # write to
    if cmd == 1 or cmd == 2:
        data = FileTransfer()
        data.operator_id = operator
        data.type = 'upload' if cmd == 1 else 'download'
        data.local = args[4]
        data.remote = args[5]
        data.start_date = star_time
        data.end_date = end_time
        data.size = size
        data.save()
        for fip in fail_server:
            data.fail_server.add(fip)

    else:
        data = Command()
        data.operator_id = operator
        data.cmd = cmd
        data.start_date = star_time
        data.end_date = end_time
        data.content = ''.join(results)
        data.save()
    for ip in ips:
        data.ip.add(ip)

    return {
        'code': 0,
        'msg': '',
        'data': results,
        'count': len(results)
    }


def chat(request):
    # with open(os.path.join(os.path.dirname(__file__), 'chat.json'), encoding='utf-8', mode='r') as f:
    #     data = json.load(f)

    user_id = json.loads(request.session[SESS_CONFIG['key']]).get('id')
    # user_id = 1
    data = _connect(user_id)
    data = {'code': 0, 'msg': '', 'data': data}

    return JsonResponse(data)


def _connect(user_id):
    """登录成功后获取好友信息"""
    mine = Account.objects.filter(id=user_id, status=1).values('id', 'username', 'sign', 'avatar')
    friend = FriendGroup.objects.filter(user=user_id).all().values('id', 'name', 'friendgroupfriend__friend__username',
                                                                   'friendgroupfriend__friend_id',
                                                                   'friendgroupfriend__friend__sign',
                                                                   'friendgroupfriend__friend__avatar')
    group = GroupAccount.objects.filter(user=user_id).all().values('group__name', 'group__avatar', 'group__id')
    mine = list(mine)
    if len(mine) == 0:
        return None

    print('mine', mine)
    print('friend', friend)
    print('group', group)
    mine[-1]['status'] = 'online'

    friend_list = []
    for f in list(friend):
        if f['friendgroupfriend__friend__username'] is not None and f['friendgroupfriend__friend_id'] is not None:
            item = {
                'username': f['friendgroupfriend__friend__username'],
                'id': f['friendgroupfriend__friend_id'],
                'avatar': f['friendgroupfriend__friend__avatar'],
                'sign': f['friendgroupfriend__friend__sign']
            }
        else:
            item = None
        parent = _getList(friend_list, 'id', f['id'])
        if parent is None:
            fri = {'groupname': f['name'], 'id': f['id'], 'list': []}
            if item is not None:
                fri['list'].append(item)

            friend_list.append(fri)
        else:
            if item is not None:
                parent['list'].append(item)

    group_list = []
    for g in list(group):
        group_list.append({
            'groupname': g['group__name'],
            'avatar': g['group__avatar'],
            'id': g['group__id']
        })

    return {
        'mine': mine[-1],
        'friend': friend_list,
        'group': group_list
    }


def _getList(list_data, key, value):
    for i in list_data:
        if i[key] == value:
            return i
    return None


# 只是源码介绍不用写入自己的代码中
def captcha_refresh(request):
    """  Return json with new captcha for ajax refresh request """
    if request.is_ajax():
        # 只接受ajax提交
        new_key = CaptchaStore.generate_key()
        data = {
            'code': 0,
            'mdg': '',
            'data': {'key': new_key, 'src': captcha_image_url(new_key)},
            'count': 1
        }
    else:
        data = {
            'code': 100011,
            'mdg': '请求错误',
            'data': {},
            'count': 0
        }
    return JsonResponse(data)


# sftp
def sftp(request):
    user_id = json.loads(request.session[SESS_CONFIG['key']]).get('id')
    if request.method == 'POST':
        page, limit = _where(request)
        # print('sftp', 'page = ', page, 'limit = ', limit)
        count = FileTransfer.objects.filter(operator_id=user_id).count()
        # print('count', count)
        data = FileTransfer.objects.filter(operator_id=user_id).all().order_by('-start_date')[
               (page - 1) * limit: page * limit].values('id', 'ip__servername', 'type', 'size', 'local', 'remote',
                                                        'fail_server__servername', 'operator__username', 'start_date',
                                                        'end_date')
        return JsonResponse({
            'code': 0,
            'msg': '',
            'data': list(data),
            'count': count
        })
    else:
        title = 'sftp record'
        detail = '文件传输记录'
        operate = [{'title': 'detail'}]
        table_url = './'
        toolbar = [{'title': 'index', 'url': ''}, {'title': 'add', 'url': "/sftp/add"}]
        return render(request, 'app01/sftp/index.html', locals())


def sftp_add(request):
    if request.method == 'POST':
        ser = str(request.POST.get('server[]', '')).strip()
        group = str(request.POST.get('group[]', '')).strip()
        operator = json.loads(request.session[SESS_CONFIG['key']]).get('id')
        local_path = request.POST.get('local', '').strip()
        remote_path = request.POST.get('remote', '').strip()
        cmd = request.POST.get('cmd', '0')
        if ser != '' and group != '' and remote_path != '' and remote_path != '' and operator and (
                cmd == '1' or cmd == '2'):
            t = corn_thread.MyThread(_command_add, (ser, group, operator, int(cmd), local_path, remote_path))
            t.start()
            return JsonResponse({
                'code': 0,
                'msg': '文件正在传输中，请稍等...',
                'data': [],
                'count': 1
            })
        else:
            return JsonResponse({
                'code': 100021,
                'msg': '参数错误',
                'data': [],
                'count': 0
            })
    else:
        title = 'sftp file'
        detail = '传输文件'
        operate = [{'title': 'detail'}]
        table_url = './'
        group = ServerGroup.objects.all().values('id', 'group_name')
        group = list(group)
        print('group', group)
        servers = Server.objects.all().values('id', 'servername')
        servers = list(servers)
        print('servers', servers)
        return render(request, 'app01/sftp/add.html', locals())


# 退出登录
def logout(request):
    del request.session[SESS_CONFIG['key']]
    return HttpResponseRedirect('/login/')


def chat_find(request):
    if request.is_ajax():
        group_id = request.POST.get('group_id', '0').strip()
        groupname = request.POST.get('groupname', '')
        user_id = request.POST.get('user_id', '0').strip()
        username = request.POST.get('username', '')
        nickname = request.POST.get('nickname', '')
        _type = request.POST.get('type', '0')
        if _type != '0':
            # 找群
            group_id = 0 if group_id == '' else group_id
            res = Group.objects.filter(Q(name=groupname) | Q(id=group_id)).all().values('id', 'name', 'avatar')
            res = list(res)
        else:
            # 找人
            user_id = 0 if user_id == '' else user_id
            res = Account.objects.filter(Q(username=username) | Q(nickname=nickname) | Q(id=user_id)).all().values(
                'id', 'username', 'avatar')
            res = list(res)
            for i in res:
                i['name'] = i.get('username')
                del i['username']

        return JsonResponse({
            'code': 0,
            'msg': '',
            'data': res,
            'count': len(res)
        })
    else:
        user_id = json.loads(request.session[SESS_CONFIG['key']]).get('id')
        group = FriendGroup.objects.filter(user_id=user_id).values('id', 'name')
        return render(request, 'app01/chat/find.html', locals())


def chat_msgbox(request):
    return render(request, 'app01/chat/msgbox.html')


def chat_agree_friend(request):
    if request.method == 'POST':
        fid = int(request.POST.get('id', 0))
        uid = int(request.POST.get('uid', 0))
        group = int(request.POST.get('group', 0))
        from_group = int(request.POST.get('from_group', 0))
        if fid and uid and group:
            with transaction.atomic():
                #  设置事务回滚的标记点
                sid = transaction.savepoint()
                data = Data()
                try:
                    friend = Friend.objects.filter(id=fid).values('proposer_id', 'friend_group_id',
                                                                  'receiver__username').first()
                    Friend.objects.filter(id=fid).update(is_read=1, status=1)
                    Notice.objects.create(sender=CHAT['username'], receiver_id=friend['proposer_id'],
                                          content=friend['receiver__username'] + CHAT['agreeFriend'],
                                          pub_date=corn_datetime.get_format_datetime())
                    insertlist = []
                    insertlist.append(
                        FriendGroupFriend(friend_id=friend['proposer_id'], friend_group_id=friend['friend_group_id']))
                    insertlist.append(FriendGroupFriend(friend_id=uid, friend_group_id=group))
                    # print('insertList', insertlist)
                    FriendGroupFriend.objects.bulk_create(insertlist)
                    transaction.savepoint_commit(sid)
                except Exception as e:
                    logger.error('chat_agree_friend ' + str(e))
                    transaction.savepoint_rollback(sid)
                    data.code = 100024
                    data.msg = '执行失败'

                return format_output(data)


def chat_refuse_friend(request):
    if request.method == 'POST':
        fid = int(request.POST.get('id'), 0)
        if fid:
            friend = Friend.objects.filter(id=fid).values('proposer_id', 'receiver__username').first()
            Friend.objects.filter(id=fid).delete()
            Notice.objects.create(sender=CHAT['username'], receiver_id=friend['proposer_id'],
                                  content=friend['receiver__username'] + CHAT['refuseFriend'],
                                  pub_date=corn_datetime.get_format_datetime())
        return format_output(Data())


def notice(request):
    limit = int(request.POST.get('limit', 5))
    update_date = corn_datetime.get_format_datetime()
    user_id = json.loads(request.session[SESS_CONFIG['key']]).get('id')
    res1 = Friend.objects.filter(receiver=user_id, status=0).all().values('id', 'proposer__username', 'friend_group_id',
                                                                          'proposer__avatar', 'proposer__id',
                                                                          'proposer__sign', 'remark', 'pub_date')[
           0: limit]
    print('user_id', user_id, 'res1', res1)

    res2 = Notice.objects.filter(receiver_id=user_id, is_read=0).all().values('id', 'sender', 'content', 'pub_date')
    print('res2', res2)
    res = list(res1) + list(res2)
    res.sort(key=lambda data: data['pub_date'])
    length = len(res)

    nids = []
    for item in res2:
        nids.append(item['id'])
    if len(nids):
        # Notice.objects.filter(id__in=nids).update(is_read=1, update_date=update_date)
        pass

    for item in res:
        print('item', item)
        if item.get('sender', None):
            pass
        else:
            item['user'] = {
                'id': item['proposer__id'],
                'username': item['proposer__username'],
                'avatar': item['proposer__avatar'],
                'sign': item['proposer__sign'],
                'groupid': item['friend_group_id'],
                'type': 'friend',
            }
            item['from'] = item['proposer__id']
            item['content'] = CHAT['applyFriend']
            item['from_group'] = 0
            del item['proposer__id']
            del item['proposer__username']
            del item['proposer__avatar']
            del item['friend_group_id']

    for item in res:
        item['pub_date'] = corn_datetime.get_timestamp_difference(int(item['pub_date'].timestamp()))
    return JsonResponse({
        'code': 0,
        'msg': '',
        'data': res,
        'count': length
    })


def test(length):
    data_list = []
    for i in range(length):
        data_list.append(random.random())

    return {
        'code': 0,
        'msg': '0',
        'data': data_list,
        'count': len(data_list)
    }


def _where(request):
    return int(request.POST.get('page', 1)), int(request.POST.get('limit', 10))


def create_password(request):
    if request.is_ajax():
        key_0 = request.POST.get('key_0', '')
        key_1 = request.POST.get('key_1', '')
        key_2 = request.POST.get('key', 0)
        if corn_tools.check_hash(key_0, key_1):
            key = corn_tools.create_salt()
            return JsonResponse({
                'code': 0,
                'msg': '',
                'data': {'key': key, 'value': corn_tools.create_password(key_2, key)},
                'count': 0
            })
        else:
            # 拒绝访问
            return JsonResponse({
                'code': 200000,
                'msg': '非法访问',
                'data': [],
                'count': 0
            })
    else:
        key_0 = corn_tools.create_salt()
        key_1 = corn_tools.create_hash(key_0)
        return render(request, 'app01/pass.html', locals())


def sendMessage(args):
    """
    保存群消息给未登录用户
    :param args: uid = args[0], to_uids = args[1] = [1, 2], data = args[2]，gid = args[3] = 0 为私聊
    :return:
    """
    print('sendMessage', args)
    res = Message.objects.create(group=int(args[3]), msg=args[2], pub_date=corn_datetime.get_format_datetime())
    if hasattr(res, 'id'):
        insert_data = []
        for uid in args[1]:
            insert_data.append(SendMessage(from_user=int(args[0]), to_user_id=int(uid), msg_id=res.id))
        SendMessage.objects.bulk_create(insert_data)


def addFriend(args):
    """
    添加好友
    :param args: uid = args[0], to_uid = args[1], group=args[2] remark = args[3]
    :return:
    """
    data = Data()
    if args[0] == args[1]:
        data.code = 100026
        data.msg = '不能添加自己为好友'
    else:
        with transaction.atomic():
            sid = transaction.savepoint()
            try:
                res = Friend.objects.filter(
                    Q(proposer_id=args[0]) & Q(receiver_id=args[1]) & ~Q(status=1) | Q(receiver_id=args[0]) & Q(
                        proposer_id=args[1]) & ~Q(status=1)).values('id')
                res = list(res)
                if len(res) != 0:
                    ids = []
                    for fid in res:
                        ids.append(fid)
                    Friend.objects.filter(id__in=ids).delete()
                Friend.objects.create(proposer_id=args[0], receiver_id=args[1], friend_group_id=args[2], remark=args[3],
                                      pub_date=corn_datetime.get_format_datetime())
            except Exception as e:
                logger.error('add friend' + str(e))
                transaction.savepoint_rollback(sid)
                data.code = 100024
                data.msg = '执行失败'
    return format_output(data)


def updateFriend(args):
    """
    更新好友状态
    :param args: uid = args[0], to_uid = args[1], type = args[2], content = args[3]
    :return:
    """
    date = corn_datetime.get_format_datetime()
    Friend.objects.filter(proposer=args[0], receiver=args[1]).update(status=args[2], update_date=date)
    Notice.objects.create(sender='系统', receiver=args[1], content=args[3], pub_date=date)


def removeFriend(args):
    """
    删除好友
    :param args: uid = args[0], to_uid = args[1], content = args[2]
    :return:
    """
    date = corn_datetime.get_format_datetime()
    Friend.objects.filter(
        Q(proposer=args[0]) & Q(receiver=args[1]) | Q(receiver=args[0]) & Q(proposer=args[1])).delete()
    Notice.objects.create(sender='系统', receiver=args[1], content=args[2], pub_date=date)


def theadDB(func=None, *args, **kwargs):
    if func is not None:
        t = corn_thread.MyThread(func, args)
        t.start()


class ChatFriendView(View):
    user = None

    def post(self, request):
        self.user = json.loads(request.session[SESS_CONFIG['key']])
        data = Data()
        _type = request.POST.get('type', None)
        if _type == '0':
            return format_output(self._delete(request, data))
        elif _type == '1':
            return format_output(self._add(request, data))
        elif _type == '2':
            return format_output(self._users(request, data))
        elif _type == '3':
            return format_output(self._remove(request, data))
        else:
            data.code = 110000
            data.msg = '请求错误'
            return format_output(data)

    def _delete(self, request, data):
        fid = int(request.POST.get('id', 0))
        with transaction.atomic():
            #  设置事务回滚的标记点
            sid = transaction.savepoint()
            try:
                FriendGroupFriend.objects.filter(friend_group_id=fid).delete()
                FriendGroup.objects.filter(id=fid).delete()
                transaction.savepoint_commit(sid)
            except Exception as e:
                logger.error('delete friend group ' + str(e))
                transaction.savepoint_rollback(sid)
                data.code = 100024
                data.msg = '执行失败'
            finally:
                return data

    def _add(self, request, data):
        name = request.POST.get('groupname', '')
        if name == '':
            data.code = 100025
            data.msg = '组名不能为空'
            return data
        user_id = self.user.get('id')
        # 创建好友分组
        res = FriendGroup.objects.filter(name=name, user_id=user_id).count()
        if res == 0:
            pub_date = corn_datetime.get_format_datetime()
            res = FriendGroup.objects.create(name=name, user_id=user_id, pub_date=pub_date)
            if hasattr(res, 'id'):
                data.data = {'id': res.id, 'groupname': name},
            else:
                data.code = 100023
                data.msg = '创建分组失败'
        else:
            data.code = 100022
            data.msg = '该名称已存在'
        return data

    def _remove(self, request, data):
        id = int(request.POST.get('id', '0'))
        fid = int(request.POST.get('fid', '0'))
        try:
            FriendGroupFriend.objects.filter(id=id).update(friend_group_id=fid)
        except Exception as e:
            logger.error('remove friend group ' + str(e))
            data.code = 100024
            data.msg = '操作失败'
        return data

    def _users(self, request, data):
        fid = int(request.POST.get('fid', 0))
        res = FriendGroupFriend.objects.filter(friend_group_id=fid).values('id', 'friend__username')
        data.data = list(res)
        data.count = len(res)
        return data


class ChatGroupView(View):
    user = None

    def post(self, request):
        self.user = json.loads(request.session[SESS_CONFIG['key']])
        data = Data()
        _type = request.POST.get('type', None)
        if _type == '0':
            return format_output(self._delete(request, data))
        elif _type == '1':
            return format_output(self._add(request, data))
        elif _type == '2':
            return format_output(self._remove(request, data))
        else:
            data.code = 110000
            data.msg = '请求错误'
            return format_output(data)

    def _delete(self, request, data):
        """解散群组"""
        fid = int(request.POST.get('id', 0))
        with transaction.atomic():
            #  设置事务回滚的标记点
            sid = transaction.savepoint()
            try:
                FriendGroupFriend.objects.filter(friend_group_id=fid).delete()
                FriendGroup.objects.filter(id=fid).delete()
                transaction.savepoint_commit(sid)
            except Exception as e:
                logger.error('delete friend group ' + str(e))
                transaction.savepoint_rollback(sid)
                data.code = 100024
                data.msg = '执行失败'
            finally:
                return data

    def _add(self, request, data):
        name = request.POST.get('groupname', '')
        if name == '':
            data.code = 100025
            data.msg = '群组名不能为空'
            return data
        # 创建好友分组
        res = Group.objects.filter(name=name).values('id').first()
        print('group ', res)
        user_id = self.user.get('id')
        pub_date = corn_datetime.get_format_datetime()
        if res is None:
            avatar = request.POST.get('avatar', '/static/images/group.png')
            with transaction.atomic():
                #  设置事务回滚的标记点
                sid = transaction.savepoint()
                try:
                    res = Group.objects.create(name=name, create_user_id=user_id, avatar=avatar, pub_date=pub_date)
                    GroupAccount.objects.create(user_id=user_id, manager=1, group_id=res.id, pub_date=pub_date)
                    transaction.savepoint_commit(sid)
                    data.data = {'id': res.id, 'groupname': name, 'avatar': avatar},
                except Exception as e:
                    logger.error('create friend group ' + str(e))
                    transaction.savepoint_rollback(sid)
                    data.code = 100023
                    data.msg = '创建群组失败'
                finally:
                    return data
        else:
            res = GroupAccount.objects.create(user_id=user_id, group_id=res.id, pub_date=pub_date)
            if res is None:
                data.code = 100023
                data.msg = '群组添加用户失败'
        return data

    def _remove(self, request, data):
        id = int(request.POST.get('id', '0'))
        user_id = int(request.POST.get('userid', '0'))
        try:
            GroupAccount.objects.filter(grou_id=id, user_id=user_id).delete()
        except Exception as e:
            logger.error('remove friend group ' + str(e))
            data.code = 100024
            data.msg = '操作失败'
        return data


def chat_group_users(request):
    """
    查看群员人数
    :param request:
    :return:
    """
    gid = int(request.GET.get('id', 0))
    users = GroupAccount.objects.filter(group_id=gid).all().values('user_id', 'user__username', 'user__avatar',
                                                                   'user__sign')
    data = Data()
    users = list(users)
    li = []
    for item in users:
        li.append({
            'id': item['user_id'],
            'username': item['user__username'],
            'name': item['user__username'],
            'avatar': item['user__avatar'],
            'sign': item['user__sign']
        })
    data.data = {'list': li}
    data.count = len(users)
    return format_output(data)


def updateSendMessage(args):
    SendMessage.objects.filter(id__in=args[0]).update(is_read=1)
