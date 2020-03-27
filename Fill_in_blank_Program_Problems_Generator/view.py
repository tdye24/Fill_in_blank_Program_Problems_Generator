# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/13 20:44
# @name:view
# @author:TDYe
from django.core import serializers
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from DBModel.models import User, Problem, Submission
from django.contrib.auth.hashers import make_password, check_password
import json


def index(request):
	"""
	firstly loads problem list and render the problem archive panel
	:param request:
	:return:
	"""
	problemList, problemVolumes = _get_problem_list(1)
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
			next = request.GET.get('next')
			if exist:
				user = User.objects.all().filter(email=email)[0]
				if check_password(password, user.password):
					request.session['checkSignin'] = True
					request.session['email'] = user.email
					request.session['nickname'] = user.nickname
					request.session['score'] = str(user.score)
					return redirect(next)
				else:
					# The password is wrong.
					return redirect(next)
			else:
				# The account does not exist.
				return render(next)
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
	problemList, problemVolumes = _get_problem_list(problemVolume)
	return render(request, 'index.html', {'problemList': problemList,
	                                      'problemVolume': problemVolume,
	                                      'problemVolumes': problemVolumes,
	                                      'problemTabClass': 'active',
	                                      'statusTabClass': '',
	                                      'rankTabClass': '',
	                                      'problemContentClass': '',
	                                      'statusContentClass': 'hidden',
	                                      'rankContentClass': 'hidden', })


def _get_problem_list(volume):
	problemList = Problem.objects.values('id', 'title', 'averageScore', 'score'). \
		              order_by('id')[(volume - 1) * 20: volume * 20]
	volumes = [(i + 1) for i in range(int(Problem.objects.count() / 20) + 1)]
	return problemList, volumes


def get_problem_by_id(request):
	"""
	get specified problem targeted by problem id
	:param request:
	:return:
	"""
	id = eval(request.GET.get('id'))
	problem = Problem.objects.values(
		'id', 'title', 'theme', 'author', 'description', 'answer', 'averageScore', 'score').filter(id=id)[0]
	problem['theme'] = problem['theme'].split(',')
	problem['blanksNums'] = [(i+1) for i in range(len(problem['answer'].split(',')))]
	del(problem['answer'])
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
	problemList = Problem.objects.filter(theme__contains=theme).values('id', 'title', 'averageScore', 'score'). \
		order_by('id')[(problemVolume - 1) * 20: problemVolume * 20]
	problemVolumes = [(i + 1) for i in range(int(Problem.objects.filter(theme__contains=theme).count() / 20) + 1)]
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
	statusList = Submission.objects.all().order_by('-runId')[(statusVolume - 1) * 20: statusVolume * 20]
	statusVolumes = [(i + 1) for i in range(int(Submission.objects.count() / 20) + 1)]
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
	ranklistVolume = eval(request.GET.get('volume'))
	ranklist = User.objects.all().order_by('-score')[(ranklistVolume - 1) * 20: ranklistVolume * 20]
	ranklistVolumes = [(i + 1) for i in range(int(User.objects.count() / 20) + 1)]
	return render(request, 'index.html', {'ranklist': ranklist,
	                                      'ranklistVolume': ranklistVolume,
	                                      'ranklistVolumes': ranklistVolumes,
	                                      'problemTabClass': '',
	                                      'statusTabClass': '',
	                                      'rankTabClass': 'active',
	                                      'problemContentClass': 'hidden',
	                                      'statusContentClass': 'hidden',
	                                      'rankContentClass': '', })


def upload_problem(request):
	pass


def submit(request):
	pass
