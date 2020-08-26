from django.contrib import admin

# Register your models here.

# from app01 import models
# admin.site.register(models.Article)
# admin.site.register(models.Account)

from .models import Account, Article, Tag, Friend, Department, Schedule, ScheduleProcess, Server, ServerGroup, Command
from .models import Blog, Attachment, FriendGroup, FriendGroupFriend, Active, Group, GroupAccount, Message, \
    SendMessage, FileTransfer


class AccountInline(admin.TabularInline):
    model = Account
    extra = 3


class AccountAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Required fields', {'fields': ['username', 'nickname', 'salt', 'password', 'group_id', 'pub_date']}),
        ('Optional fields', {'fields': ['email', 'phone', 'avatar', 'state', 'create_user_id', 'update_date']})
    ]
    list_display = ('username', 'nickname', 'email', 'phone', 'group_id', 'status', 'state', 'pub_date')
    list_filter = ['pub_date']
    search_fields = ['username', 'email', 'phone']


class ArticleAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Article relation', {'fields': ['title', 'author', 'content', 'tags', 'image_path']}),
        ('Hide', {'fields': ['read_count', 'pub_date']})
    ]
    list_display = ('id', 'title', 'author', 'content_clips', 'tags_text', 'image_path', 'read_count', 'pub_date')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pub_date')
    # list_display = ('id', 'name')


class FriendAdmin(admin.ModelAdmin):
    # list_display_links = None
    list_display = ('proposer', 'receiver', 'status', 'is_read', 'is_pro_del', 'is_rec_del', 'pub_date')

    # def has_add_permission(self, request):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    # def has_change_permission(self, request, obj=None):
    #     return False


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'pub_date')


class ServerGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name', 'department', 'pub_date')


class ServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'servername', 'ip', 'username', 'skey', 'status', 'group_id', 'deny_users', 'pub_date')

    def deny_users(self, obj):
        return [bt for bt in obj.deny_user.all()]

    filter_horizontal = ('deny_user',)


class FileTransferAdmin(admin.ModelAdmin):
    list_display = ('id', 'server', 'type', 'local', 'remote', 'size', 'fail_servers', 'operator', 'start_date', 'end_date')

    def server(self, obj):
        return [s for s in obj.ip.all()]

    def fail_servers(self, obj):
        return [f for f in obj.fail_server.all()]

    filter_horizontal = ('ip', 'fail_server', )


class FriendGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'pub_date')


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ServerGroup, ServerGroupAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Schedule)
admin.site.register(ScheduleProcess)
admin.site.register(Command)
admin.site.register(Friend, FriendAdmin)
admin.site.register(Group)
admin.site.register(GroupAccount)
admin.site.register(FriendGroup, FriendGroupAdmin)
admin.site.register(FriendGroupFriend)
admin.site.register(Attachment)
admin.site.register(Blog)
admin.site.register(Active)
admin.site.register(Message)
admin.site.register(SendMessage)
admin.site.register(FileTransfer, FileTransferAdmin)
