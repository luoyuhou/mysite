#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/6/20
# Time:     11:30
# IDE :     PyCharm

from django.urls import path
from . import views

app_name = 'app01'  # 添加命名空间

# urlpatterns = [
#     path('', views.index, name='index'),
#     path('<int:question_id>/', views.detail, name='detail'),
#     path('<int:question_id>/results/', views.results, name='results'),
#     path('<int:question_id>/vote/', views.vote, name='vote')
# ]
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('article/', views.article, name='article'),
    path('home/', views.home, name='home'),
    path('home/add/', views.home_add, name='home_add'),
    path('upload/image/', views.upload_image, name='upload_image'),
    path('upload/rimage/', views.upload_rimage, name='upload_rimage'),
    path('upload/mimage/', views.upload_multiple_image, name='multiple_image'),
    path('upload/image_lay/', views.upload_image_lay, name='upload_image_lay'),
    path('attachment/', views.attachment, name='attachment'),
    path('active/', views.active, name='active'),
    path('active/get/', views.active_get, name='active_get'),
    path('blog/', views.blog, name='blog'),
    path('blog/<int:user_id>/', views.blog_view, name='blog_view'),
    path('blog/edit/', views.blog_edit, name='blog_edit'),
    path('blog/add/', views.blog_add, name='blog_add'),
    path('command/', views.command, name='command'),
    path('command/add/', views.command_add, name='command_add'),
    path('chat/', views.chat, name='chat'),
    path('chat/msgbox/', views.chat_msgbox, name='chat_msgbox'),
    path('chat/msgbox/notice/', views.notice, name='chat_notice'),
    path('chat/find/', views.chat_find, name='chat_find'),
    path('chat/agreeFriend/', views.chat_agree_friend, name='chat_agree_friend'),
    path('chat/refuseFriend/', views.chat_refuse_friend, name='chat_refuse_friend'),
    # path('chat/find/create/', views.chat_create, name='chat_create'),
    # path('chat/find/create/', views.chat_create, name='chat_create'),
    path('chat/friend/', views.ChatFriendView.as_view(), name='chat_friend'),
    path('chat/group/', views.ChatGroupView.as_view(), name='chat_group'),
    path('chat/group/users/', views.chat_group_users, name='chat_group_users'),
    path('captcha/refresh/', views.captcha_refresh, name='captcha_refresh'),
    path('logout/', views.logout, name='logout'),
    path('sftp/', views.sftp, name='sftp'),
    path('sftp/add/', views.sftp_add, name='sftp_add'),
    path('ababc6b2744814ddacbaf1bfd1739fcee37afc33a6d08a411d66bfc3b512326b/', views.create_password, name='create_password'),
]
