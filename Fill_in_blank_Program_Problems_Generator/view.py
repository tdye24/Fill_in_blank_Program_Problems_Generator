# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/13 20:44
# @name:view
# @author:TDYe
import json
import os
from .tools import unzip_file
from django.core import serializers
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from DBModel.models import User, Problem, Submission, Teacher
from django.contrib.auth.hashers import make_password, check_password


def index(request):
	"""
	firstly loads problem list and render the problem archive panel
	:param request:
	:return:
	"""
	problemList = Problem.get_problem_list(volume=1)
	problemVolumes = Problem.get_problem_volumes()
	return render(request, 'index.html', {
								'problemList': problemList,
								'problemVolume': 1,
								'problemVolumes': problemVolumes,
								'problemTabClass': 'active',
								'statusTabClass': '',
								'rankTabClass': '',
								'problemContentClass': '',
								'statusContentClass': 'hidden',
								'rankContentClass': 'hidden', })


def user(request):
	"""
	user signup, signin, checkLogin/
	:param request:
	:return:
	"""
	if request.method == 'POST':
		if request.GET.get('action') == 'signin':
			email = request.POST.get('email')
			password = request.POST.get('password')
			exist = User.objects.filter(email=email).exists()
			nextURL = request.GET.get('next')
			if exist:
				user = User.objects.all().filter(email=email)[0]
				if check_password(password, user.password):
					request.session['checkSignin'] = True
					request.session['email'] = user.email
					request.session['nickname'] = user.nickname
					request.session['score'] = str(user.score)
					return redirect(nextURL)
				else:
					# The password is wrong.
					return redirect(nextURL)
			else:
				# The account does not exist.
				return redirect(nextURL)
		elif request.GET.get('action') == 'signup':
			email, password, nickname \
				= request.POST.get('email'), request.POST.get('password'), request.POST.get('nickname')
			try:
				user = User(email=email,
				            password=make_password(password=password, salt=None),
				            nickname=nickname)
				user.save()
				next = request.GET.get('next')
				return redirect(next)
			except ValueError:
				print("Invalid parameters => (email, password, nickname)")
		else:
			return render(request, 'register.html')
	elif request.method == 'GET':
		if request.GET.get('action') == 'logout':
			nextURL = request.GET.get('next')
			request.session['checkSignin'] = False
			request.session['email'] = ''
			request.session['nickname'] = ''
			request.session['score'] = ''
			return redirect(nextURL)


def register(request):
	"""
	just render the register.html, the register process wid handled by view.user?action=signup&next=...
	:param
	:return:
	"""
	if request.method == 'GET':
		# next：the url for redirecting after registration
		return render(request, 'register.html', {'next': request.GET.get('next')})


def get_problem_list(request):
	"""
	get problem list consisting of maximum 20 problems
	:param request:
	:return:
	"""
	problemVolume = eval(request.GET.get('volume'))
	problemList = Problem.get_problem_list(volume=problemVolume)
	problemVolumes = Problem.get_problem_volumes()
	return render(request, 'index.html', {'problemList': problemList,
	                                      'problemVolume': problemVolume,
	                                      'problemVolumes': problemVolumes,
	                                      'problemTabClass': 'active',
	                                      'statusTabClass': '',
	                                      'rankTabClass': '',
	                                      'problemContentClass': '',
	                                      'statusContentClass': 'hidden',
	                                      'rankContentClass': 'hidden', })


def get_problem_by_id(request):
	"""
	get specified problem targeted by problem id
	:param request:
	:return:
	"""
	id = eval(request.GET.get('id'))
	problem = Problem.get_problem_by_id(id=id)
	return render(request, 'problem.html', {'problem': problem,
	                                        'problemTabClass': 'active',
	                                        'statusTabClass': '',
	                                        'rankTabClass': '',
	                                        'problemContentClass': '',
	                                        'statusContentClass': 'hidden',
	                                        'rankContentClass': 'hidden', })


def get_problem_by_keyword(request):
	keyword = request.GET.get('keyword')
	print(keyword)
	pass


def get_problem_by_theme(request):
	"""
	get a collection of questions having the common tag or theme
	:param request:
	:return:
	"""
	theme = request.GET.get('theme')
	problemVolume = eval(request.GET.get('volume'))
	problemList = Problem.get_problem_list_by_theme(theme=theme, problemVolume=problemVolume)
	problemVolumes = Problem.get_problem_volumes_by_theme(theme=theme)
	return render(request, 'theme.html', {
							'problemList': problemList,
	                        'theme': theme,
	                        'problemVolume': problemVolume,
	                        'problemVolumes': problemVolumes,
							'problemTabClass': 'active',
							'statusTabClass': '',
							'rankTabClass': '',
							'problemContentClass': '',
							'statusContentClass': 'hidden',
							'rankContentClass': 'hidden', })


def get_status_list(request):
	"""
	get judge status list
	:param request:
	:return:
	"""
	statusVolume = eval(request.GET.get('volume'))
	statusList = Submission.get_status_list(statusVolume=statusVolume)
	statusVolumes = Submission.get_status_volumes()
	return render(request, 'index.html', {'statusList': statusList,
	                                      'statusVolume': statusVolume,
	                                      'statusVolumes': statusVolumes,
	                                      'problemTabClass': '',
	                                      'statusTabClass': 'active',
	                                      'rankTabClass': '',
	                                      'problemContentClass': 'hidden',
	                                      'statusContentClass': '',
	                                      'rankContentClass': 'hidden', })


def get_ranklist(request):
	"""
	get rank list
	:param request:
	:return:
	"""
	ranklistVolume = eval(request.GET.get('volume'))
	ranklist = User.get_ranklist(ranklistVolume=ranklistVolume)
	ranklistVolumes = User.get_ranklist_volumes()
	return render(request, 'index.html', {'ranklist': ranklist,
	                                      'ranklistVolume': ranklistVolume,
	                                      'ranklistVolumes': ranklistVolumes,
	                                      'problemTabClass': '',
	                                      'statusTabClass': '',
	                                      'rankTabClass': 'active',
	                                      'problemContentClass': 'hidden',
	                                      'statusContentClass': 'hidden',
	                                      'rankContentClass': '', })


def submit(request):
	pass


def teacher_index(request):
	return render(request, 'teacher_index.html')


def teacher(request):
	"""
	teacher signup, signin, checkLogin/
	:param request:
	:return:
	"""
	if request.method == 'POST':
		if request.GET.get('action') == 'signin':
			email = request.POST.get('email')
			password = request.POST.get('password')
			exist = Teacher.objects.filter(email=email).exists()
			nextURL = request.GET.get('next')
			if exist:
				teacher = Teacher.objects.all().filter(email=email)[0]
				if check_password(password, teacher.password):
					request.session['checkTeacherSignin'] = True
					request.session['teacherEmail'] = teacher.email
					request.session['teacherNickname'] = teacher.nickname
					return redirect(nextURL)
				else:
					# The password is wrong.
					return redirect(nextURL)
			else:
				# The account does not exist.
				return render(nextURL)
		elif request.GET.get('action') == 'upload':
			title = request.POST.get('title')
			themes = request.POST.get('themes')
			description = request.POST.get('description')
			print('title', title)
			print('themes', themes)
			print('description', description)
			id = Problem.get_next_problem_id()
			filename = "%s%s" % (str(id), '.cpp')
			print('id', id)
			problem_file_obj = request.FILES.get('problem-file')
			problem_file_path = os.path.join('data/problem', filename)
			f = open(problem_file_path, mode="wb")
			for i in problem_file_obj.chunks():     # TODO(tdye): using coroutine?
				f.write(i)
			f.close()
			test_cases_obj = request.FILES.get('test-cases')
			if not os.path.exists("%s%s" % ('data/test_cases/', str(id))):
				os.mkdir("%s%s" % ('data/test_cases/', str(id)))
			else:
				print('directory already exists')
				return False
			test_cases_path_rar = os.path.join('data/test_cases', str(id), str(id)+'.zip')
			test_cases_path = os.path.join('data/test_cases', str(id))
			f = open(test_cases_path_rar, mode="wb")
			for i in test_cases_obj.chunks():  # TODO(tdye): using coroutine?
				f.write(i)
			f.close()
			unzip_file(test_cases_path_rar, test_cases_path)
			os.remove(test_cases_path_rar)
			return render(request, 'upload.html', {})
	elif request.method == 'GET':
		if request.GET.get('action') == 'logout':
			nextURL = request.GET.get('next')
			request.session['checkTeacherSignin'] = False
			request.session['teacherEmail'] = ''
			request.session['teacherNickname'] = ''
			return redirect(nextURL)


def upload(request):
	return render(request, 'upload.html', {})


def upload_problem(request):
	email = request.POST.get('email')
