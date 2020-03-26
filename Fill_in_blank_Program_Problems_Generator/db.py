# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/23 12:17
# @name:db
# @author:TDYe
import json
from django.http import HttpResponse
from DBModel.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render


