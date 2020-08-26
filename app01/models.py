from django.db import models


# Create your models here.
class Department(models.Model):
    """部门表
    name 部门名称
    """
    name = models.CharField(max_length=30, unique=True)
    pub_date = models.DateTimeField()

    def __str__(self):
        return self.name


class Account(models.Model):
    """账号表
    state 加好友是否需要直接添加，0 需要对方同意，1 直接加好友
    manager 是否是管理者
    status 账号是否可用，1 正常使用，0 禁止使用
    group_id 属于的部门
    """
    username = models.CharField(max_length=50, unique=True)
    nickname = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=64)
    email = models.EmailField(blank=True)
    avatar = models.CharField(max_length=50, blank=True, default='/static/images/avatar.png')
    salt = models.CharField(max_length=6, blank=True)
    sign = models.CharField(max_length=50, blank=True, default='这个人很懒，什么也没说！')
    pub_date = models.DateTimeField()
    phone = models.CharField(max_length=12, blank=True)
    state = models.BooleanField(default=0)
    manager = models.BooleanField(default=0)
    status = models.BooleanField(default=1)
    group_id = models.ForeignKey(Department, verbose_name='Department', on_delete=models.CASCADE)
    create_user_id = models.IntegerField(blank=True)
    update_date = models.DateTimeField(blank=True)

    def __str__(self):
        return self.username


class FriendGroup(models.Model):
    """好友分组表

    """
    user = models.ForeignKey(Account, verbose_name='Account', on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    pub_date = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return str(self.user) + '__' + self.name


class Friend(models.Model):
    """
    好友表
    proposer 申请好友用于的 id
    receiver 被申请加好友的用户 id
    status 好友申请状态 0 申请 1 同意 2 拒绝
    is_pro_del 好友关系状态 0 关系不错 1 申请者删除好友
    is_rec_del 好友关系状态 0 关系不错 1 被申请者删除好友
    """
    proposer = models.ForeignKey(Account, verbose_name='申请者', related_name='friend_proposer', on_delete=models.CASCADE)
    receiver = models.ForeignKey(Account, verbose_name='接受者', on_delete=models.CASCADE)
    remark = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=0)
    status = models.BooleanField(default=0)
    is_pro_del = models.BooleanField(default=0)
    is_rec_del = models.BooleanField(default=0)
    friend_group = models.ForeignKey(FriendGroup, verbose_name='分组', on_delete=models.CASCADE)
    pub_date = models.DateTimeField()
    update_date = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('proposer', 'receiver')

    # def proposer(self):
    #     return Account.objects.get(id=self.proposer_id).username
    #
    # def receive(self):
    #     return Account.objects.get(id=self.receiver_id).username


class Notice(models.Model):
    sender = models.CharField(max_length=50)
    receiver = models.ForeignKey(Account, verbose_name='接受者', on_delete=models.CASCADE)
    content = models.CharField(max_length=255)
    is_read = models.BooleanField(default=0)
    pub_date = models.DateTimeField()
    update_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.content


class FriendGroupFriend(models.Model):
    friend_group = models.ForeignKey(FriendGroup, verbose_name='FriendGroup', on_delete=models.CASCADE)
    friend = models.ForeignKey(Account, verbose_name='Account', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('friend_group', 'friend')


class Article(models.Model):
    """文章表"""
    author = models.ForeignKey('Account', verbose_name='作者', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    image_path = models.CharField(max_length=255)
    tags = models.ManyToManyField('Tag', blank=True)
    pub_date = models.DateTimeField()
    read_count = models.IntegerField()

    def __str__(self):
        return self.title

    def content_clips(self):
        return self.content[0:10]

    def tags_text(self):
        print(self.tags)
        return '123'


class Tag(models.Model):
    """文章标签表"""
    name = models.CharField(max_length=10, unique=True)
    status = models.BooleanField(default=1)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Schedule(models.Model):
    """工作机会表"""
    publisher = models.ForeignKey(Account, verbose_name='发布者', on_delete=models.CASCADE)
    title = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    image_path = models.CharField(max_length=255)
    status = models.BooleanField()
    urgent = models.BooleanField()
    pub_date = models.DateTimeField()
    deadline = models.DateTimeField()

    def __str__(self):
        return self.title


class ScheduleProcess(models.Model):
    schedule = models.ForeignKey(Schedule, verbose_name='任务', on_delete=models.CASCADE)
    operator = models.CharField(max_length=50)
    status = models.BooleanField()
    content = models.TextField()
    image_path = models.CharField(max_length=255)
    pub_date = models.DateTimeField()

    def __str__(self):
        return self.schedule_id


class Attachment(models.Model):
    filename = models.CharField(max_length=100, unique=True)
    file_path = models.CharField(max_length=255)
    size = models.IntegerField()
    hash = models.CharField(max_length=255, unique=True)
    pub_date = models.DateTimeField()
    ip = models.CharField(max_length=20)
    operator = models.CharField(max_length=50, default=0)

    def __str__(self):
        return self.filename


class Active(models.Model):
    content = models.TextField()
    image_path = models.CharField(max_length=255)
    operator = models.ForeignKey(Account, verbose_name='操作者', on_delete=models.CASCADE)
    ip = models.CharField(max_length=20)
    pub_date = models.DateTimeField()

    def __str__(self):
        return self.content


class Blog(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    operator = models.ForeignKey(Account, verbose_name='操作者', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    public = models.BooleanField()
    pub_date = models.DateTimeField()

    class Meta:
        unique_together = ('title', 'operator')

    def __str__(self):
        return self.title

    def content_clips(self):
        return self.content[0:10]


class ServerGroup(models.Model):
    """服务器分组表
    group_name 分组名称
    department 属于哪个部门
    """
    group_name = models.CharField(max_length=30)
    department = models.ForeignKey(Department, verbose_name='部门', on_delete=models.CASCADE)
    pub_date = models.DateTimeField()

    class Meta:
        unique_together = ('group_name', 'department')

    def __str__(self):
        return self.group_name


class Server(models.Model):
    """服务器表
    ip 服务器的 ip
    servername 服务器的名称，默认为 ip
    username 服务器登录账号
    password 服务器登录密码
    skey 是否使用秘钥免密码登录
    status 状态，1 可用，0 禁用
    group_id 服务器属于哪个组
    deny_user 那些用户被禁用
    """
    ip = models.CharField(max_length=30)
    servername = models.CharField(max_length=30)
    username = models.CharField(max_length=20, default='')
    password = models.CharField(max_length=50, default='')
    skey = models.BooleanField(default=0)
    status = models.BooleanField()
    group_id = models.ForeignKey(ServerGroup, verbose_name='分组id', on_delete=models.CASCADE)
    pub_date = models.DateTimeField()
    deny_user = models.ManyToManyField(Account, blank=True)

    class Meta:
        unique_together = ('ip', 'group_id')

    def __str__(self):
        return self.servername


class Command(models.Model):
    """远程执行命令表
    cmd 执行的命令
    ip 执行操作的 服务器
    content 执行返回的结果
    operator 操作者
    start_date 执行开始时间
    end_date 执行结束的时间
    """
    cmd = models.CharField(max_length=255)
    ip = models.ManyToManyField(Server)
    content = models.TextField()
    operator = models.ForeignKey(Account, verbose_name='操作者', on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.cmd

    def content_clips(self):
        return self.content[0:10]


class Group(models.Model):
    """讨论组"""
    name = models.CharField(max_length=20, unique=True)
    avatar = models.CharField(max_length=50, blank=True)
    create_user = models.ForeignKey(Account, verbose_name='create user', on_delete=models.CASCADE)
    pub_date = models.DateTimeField()


class GroupAccount(models.Model):
    user = models.ForeignKey(Account, verbose_name='user', on_delete=models.CASCADE)
    manager = models.BooleanField(default=0)
    group = models.ForeignKey(Group, verbose_name='group', on_delete=models.CASCADE)
    pub_date = models.DateTimeField()

    class Meta:
        unique_together = ('user', 'group')


class Message(models.Model):
    """消息表
    group 消息来自于哪个表，0 为私聊
    msg 消息内容
    status 消息是否可用
    """
    group = models.IntegerField(default=0)
    msg = models.TextField()
    status = models.BooleanField(default=1)
    pub_date = models.DateTimeField()


class SendMessage(models.Model):
    from_user = models.IntegerField(default=0)
    to_user = models.ForeignKey(Account, verbose_name='接受者', on_delete=models.CASCADE)
    msg = models.ForeignKey(Message, verbose_name='message', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=0)


class FileTransfer(models.Model):
    operator = models.ForeignKey(Account, verbose_name='操作者', on_delete=models.CASCADE)
    type = models.CharField(max_length=10)
    ip = models.ManyToManyField(Server, related_name='server')
    fail_server = models.ManyToManyField(Server)
    local = models.CharField(max_length=255)
    remote = models.CharField(max_length=255)
    size = models.IntegerField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

