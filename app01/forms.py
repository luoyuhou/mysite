#!/usr/bin/python
# -*- coding: UTF-8 -*-
# User:     worky
# Date:     2020/7/9
# Time:     14:56
# IDE :     PyCharm

from django import forms
from captcha.fields import CaptchaField


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=6, error_messages={'invalid': '密码太短'})
    captcha = CaptchaField(required=True, error_messages={'invalid': '验证码错误'})
