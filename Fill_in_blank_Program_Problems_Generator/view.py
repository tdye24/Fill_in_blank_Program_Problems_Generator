# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/3/13 20:44
# @name:view
# @author:TDYe
import os
import json

from django.http import HttpResponse

from Model.vector2program import clean_c_style
from django.shortcuts import render, redirect
from DBModel.models import User, Problem, Submission, Teacher, Admin
from django.contrib.auth.hashers import make_password, check_password
from Model import program2vector, vector2program, predict
from .tools import unzip_file
from logfile import logger
from judger.tools import read_out


def index(request):
	"""
	firstly loads problem list and render the problem archive panel
	:param request:
	:return:
	"""
	problemList = Problem.get_problem_list(volume=1)
	problemVolumes = Problem.get_problem_volumes()
	submissions = []
	if 'checkSignin' in request.session and request.session['checkSignin']:
		email = request.session['email']
		user = User.objects.all().filter(email=email)[0]
		request.session['score'] = str(user.score)
		for item in User.get_my_submissions(email=email, volume=1):
			item['score'] = str("%.2f" % item['score'])
			submissions.append(item)
	return render(request, 'index.html', {
		'problemList': problemList,
		'problemVolume': 1,
		'problemVolumes': problemVolumes,
		'problemTabClass': 'active',
		'statusTabClass': '',
		'rankTabClass': '',
		'problemContentClass': '',
		'statusContentClass': 'hidden',
		'rankContentClass': 'hidden',
		'submissions': submissions, })


def user(request):
	"""
	user signup, signin, checkSignin/
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
					submissions = []
					for item in User.get_my_submissions(email=email, volume=1):
						item['score'] = str("%.2f" % item['score'])
						submissions.append(item)
					request.session['submissions'] = json.dumps(submissions)
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
				print("Invalid parameters => (%s, %s, %s) while saving a user!" % (email, password, nickname))
				logger.error("Invalid parameters => (%s, %s, %s) while saving a user!" % (email, password, nickname))
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


def get_problem_list_by(request):
	if request.method == 'GET':
		way = request.GET.get('way')
		query = request.GET.get('query')
		data = request.GET.copy()
		if way == 'id':
			data['id'] = query
			request.GET = data
			return get_problem_by_id(request)
		elif way == 'title':
			data['keyword'] = query
			data['volume'] = '1'
			request.GET = data
			return get_problem_by_keyword(request)
		elif way == 'theme':
			from Model.themes import themes
			flag = True
			for key in themes:
				if themes[key] == query:
					query = key
					flag = False
					break
			if flag:
				return redirect('/getProblemList?volume=1')
			data['theme'] = query
			data['volume'] = '1'
			request.GET = data
			return get_problem_by_theme(request)


def get_problem_list(request):
	"""
	get problem list consisting of maximum 20 problems
	:param request:
	:return:
	"""
	problemVolume = eval(request.GET.get('volume'))
	problemList = Problem.get_problem_list(volume=problemVolume)
	problemVolumes = Problem.get_problem_volumes()
	submissions = []
	if 'checkSignin' in request.session and request.session['checkSignin']:
		email = request.session['email']
		user = User.objects.all().filter(email=email)[0]
		request.session['score'] = str(user.score)
		for item in User.get_my_submissions(email=email, volume=1):
			item['score'] = str("%.2f" % item['score'])
			submissions.append(item)
	return render(request, 'index.html', {'problemList': problemList,
	                                      'problemVolume': problemVolume,
	                                      'problemVolumes': problemVolumes,
	                                      'problemTabClass': 'active',
	                                      'statusTabClass': '',
	                                      'rankTabClass': '',
	                                      'problemContentClass': '',
	                                      'statusContentClass': 'hidden',
	                                      'rankContentClass': 'hidden',
	                                      'submissions': submissions, })


def get_problem_by_id(request):
	"""
	get specified problem targeted by problem id
	:param request:
	:return:
	"""
	try:
		id = eval(request.GET.get('id'))
	except Exception as e:
		print(e, "\nIncorrect Way")
		return redirect('/getProblemList?volume=1')
	problem = Problem.get_problem_by_id(id=id)
	problemFile = read_out('data/problem/' + str(id) + '.cpp')
	sampleIn = read_out('data/test_cases/' + str(id) + '/1.in')
	# sampleIn = sampleIn.replace('\n', '<br/>')
	sampleOut = read_out('data/test_cases/' + str(id) + '/1.out')
	# sampleOut = sampleOut.replace('\n', '<br/>')
	submissions = []
	if 'checkSignin' in request.session and request.session['checkSignin']:
		email = request.session['email']
		user = User.objects.all().filter(email=email)[0]
		request.session['score'] = str(user.score)
		for item in User.get_my_submissions(email=email, volume=1):
			item['score'] = str("%.2f" % item['score'])
			submissions.append(item)
	return render(request, 'problem.html', {'problem': problem,
	                                        'problemFile': problemFile,
	                                        'sampleIn': sampleIn,
	                                        'sampleOut': sampleOut,
	                                        'problemTabClass': 'active',
	                                        'statusTabClass': '',
	                                        'rankTabClass': '',
	                                        'problemContentClass': '',
	                                        'statusContentClass': 'hidden',
	                                        'rankContentClass': 'hidden',
	                                        'submissions': submissions, })


def get_problem_by_keyword(request):
	keyword = request.GET.get('keyword')
	problemVolume = eval(request.GET.get('volume'))
	problemList = Problem.get_problem_list_by_keyword(keyword=keyword, problemVolume=problemVolume)
	problemVolumes = Problem.get_problem_volumes_by_keyword(keyword=keyword)
	submissions = []
	if 'checkSignin' in request.session and request.session['checkSignin']:
		email = request.session['email']
		user = User.objects.all().filter(email=email)[0]
		request.session['score'] = str(user.score)
		for item in User.get_my_submissions(email=email, volume=1):
			item['score'] = str("%.2f" % item['score'])
			submissions.append(item)
	return render(request, 'keyword.html', {
		'problemList': problemList,
		'keyword': keyword,
		'problemVolume': problemVolume,
		'problemVolumes': problemVolumes,
		'problemTabClass': 'active',
		'statusTabClass': '',
		'rankTabClass': '',
		'problemContentClass': '',
		'statusContentClass': 'hidden',
		'rankContentClass': 'hidden',
		'submissions': submissions, })


def get_problem_by_theme(request):
	"""
	get a collection of questions having the common tag or theme
	:param request:
	:return:
	"""
	from Model.themes import themes
	theme = request.GET.get('theme')
	problemVolume = eval(request.GET.get('volume'))
	problemList = Problem.get_problem_list_by_theme(theme=theme, problemVolume=problemVolume)
	problemVolumes = Problem.get_problem_volumes_by_theme(theme=theme)
	submissions = []
	if 'checkSignin' in request.session and request.session['checkSignin']:
		email = request.session['email']
		user = User.objects.all().filter(email=email)[0]
		request.session['score'] = str(user.score)
		for item in User.get_my_submissions(email=email, volume=1):
			item['score'] = str("%.2f" % item['score'])
			submissions.append(item)
	return render(request, 'theme.html', {
		'problemList': problemList,
		'themeId': theme,
		'theme': themes[theme],
		'problemVolume': problemVolume,
		'problemVolumes': problemVolumes,
		'problemTabClass': 'active',
		'statusTabClass': '',
		'rankTabClass': '',
		'problemContentClass': '',
		'statusContentClass': 'hidden',
		'rankContentClass': 'hidden',
		'submissions': submissions, })


def get_status_list(request):
	"""
	get judge status list
	:param request:
	:return:
	"""
	statusVolume = eval(request.GET.get('volume'))
	statusList = Submission.get_status_list(statusVolume=statusVolume)
	for it in statusList:
		it['score'] = str("%.2f" % it['score'])
	statusVolumes = Submission.get_status_volumes()
	submissions = []
	if 'checkSignin' in request.session and request.session['checkSignin']:
		email = request.session['email']
		user = User.objects.all().filter(email=email)[0]
		request.session['score'] = str(user.score)
		for item in User.get_my_submissions(email=email, volume=1):
			item['score'] = str("%.2f" % item['score'])
			submissions.append(item)
	return render(request, 'index.html', {'statusList': statusList,
	                                      'statusVolume': statusVolume,
	                                      'statusVolumes': statusVolumes,
	                                      'problemTabClass': '',
	                                      'statusTabClass': 'active',
	                                      'rankTabClass': '',
	                                      'problemContentClass': 'hidden',
	                                      'statusContentClass': '',
	                                      'rankContentClass': 'hidden',
	                                      'submissions': submissions, })


def get_ranklist(request):
	"""
	get rank list
	:param request:
	:return:
	"""
	ranklistVolume = eval(request.GET.get('volume'))
	ranklist = User.get_ranklist(ranklistVolume=ranklistVolume)
	ranklistVolumes = User.get_ranklist_volumes()
	submissions = []
	if 'checkSignin' in request.session and request.session['checkSignin']:
		email = request.session['email']
		user = User.objects.all().filter(email=email)[0]
		request.session['score'] = str(user.score)
		for item in User.get_my_submissions(email=email, volume=1):
			item['score'] = str("%.2f" % item['score'])
			submissions.append(item)
	return render(request, 'index.html', {'ranklist': ranklist,
	                                      'ranklistVolume': ranklistVolume,
	                                      'ranklistVolumes': ranklistVolumes,
	                                      'problemTabClass': '',
	                                      'statusTabClass': '',
	                                      'rankTabClass': 'active',
	                                      'problemContentClass': 'hidden',
	                                      'statusContentClass': 'hidden',
	                                      'rankContentClass': '',
	                                      'submissions': submissions, })


def submit(request):
	if 'checkSignin' in request.session and request.session['checkSignin']:
		email = request.session['email']
		# nickname = request.session['nickname']
		submission = []
		for key in request.POST.keys():
			submission.append(request.POST.get(key))
		proId = eval(request.GET.get('proId'))
		jsonDataPath = 'data\\jsonData\\%s.json' % str(proId)
		with open(jsonDataPath) as f:
			X0 = (json.load(f))[0]
		raw_tokens = [item[0] for item in X0]
		problemInfo = Problem.objects.values('answer', 'blanks').filter(id=proId)[0]
		# answer_lst = json.loads(problemInfo['answer'])
		# TODO(tdye): not used answer_lst
		blanks_lst = json.loads(problemInfo['blanks'])
		i = 0
		submissionId = Submission.get_next_submission_id()
		logger.info(submission)
		while i < len(blanks_lst):
			temp = raw_tokens[:]
			submissionPath = 'data\\submissions\\%d-%d-%d.cpp' % (submissionId, proId, i + 1)
			temp[blanks_lst[i]] = submission[i]
			assembleContent = ''
			for item in temp:
				assembleContent += item + ' '
			with open(submissionPath, 'w') as f:
				logger.info('\n' + clean_c_style(assembleContent) + '\n')
				f.write(clean_c_style(assembleContent))
			logger.info(raw_tokens)
			logger.info(temp)
			i += 1
		try:
			dbSubmission = Submission(submissionId=submissionId, judgeStatus=-2, proId=proId, email=email,
			                          answer=json.dumps(submission))
			dbSubmission.save()
		except IOError as e:
			logger.error(e)
			logger.error('IO Error occurs while saving a new Submission %d' % submissionId)
		finally:
			return redirect('/getStatusList?volume=1')
	else:
		# request.session['errmsg'] = 'Please Login First'
		return render(request, 'upload.html', {})


def teacher(request):
	"""
	teacher signup, signin, checkTeacherSignin/
	:param request:
	:return:
	"""
	if request.method == 'GET':
		if request.GET.get('action') is None:
			repository = []
			if 'checkTeacherSignin' in request.session and request.session['checkTeacherSignin']:
				email = request.session['teacherEmail']
				for item in Teacher.get_my_repository(email=email, volume=1):
					item['averageScore'] = str(item['averageScore'])
					item['score'] = str("%.2f" % item['score'])
					repository.append(item)
			problemDB = Problem.objects.values('theme')
			problemDBInfo = {}
			from Model.themes import themes
			for problem in problemDB:
				themeList = (problem['theme']).split(',')
				for theme in themeList:
					theme = themes[theme]
					if theme in problemDBInfo.keys():
						problemDBInfo[theme] += 1
					else:
						problemDBInfo[theme] = 1
			return render(request, 'teacher_index.html', {'repository': repository,
			                                              'problemDBInfo': problemDBInfo})
		elif request.GET.get('action') == 'logout':
			nextURL = request.GET.get('next')
			request.session['checkTeacherSignin'] = False
			request.session['teacherEmail'] = ''
			request.session['teacherNickname'] = ''
			return redirect(nextURL)
	elif request.method == 'POST':
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
					repository = []
					for item in Teacher.get_my_repository(email=email, volume=1):
						item['averageScore'] = str(item['averageScore'])
						item['score'] = str("%.2f" % item['score'])
						repository.append(item)
					request.session['repository'] = json.dumps(repository)
					return redirect(nextURL)
				else:
					# The password is wrong.
					return redirect(nextURL)
			else:
				# The account does not exist.
				return redirect(nextURL)
		elif request.GET.get('action') == 'upload':
			title, themes, description, score, author = \
				request.POST.get('title'), \
				request.POST.get('themes'), \
				request.POST.get('description'), \
				int(request.POST.get('score')), \
				request.session['teacherEmail']
			themes_ = themes.split(',')
			id = Problem.get_next_problem_id()
			origin_filename = "%s-origin%s" % (str(id), '.cpp')
			problem_filename = "%s%s" % (str(id), '.cpp')
			jsonData_filename = "%s%s" % (str(id), '.json')
			problem_file_obj = request.FILES.get('problem-file')
			origin_file_path = os.path.join('data\\problem', origin_filename)
			problem_file_path = os.path.join('data\\problem', problem_filename)

			f = open(origin_file_path, mode="wb")
			for i in problem_file_obj.chunks():  # TODO(tdye): using coroutine?
				f.write(i)
			f.close()
			X = program2vector.transform(origin_file_path)
			jsonDataPath = os.path.join('data\\jsonData', jsonData_filename)
			with open(jsonDataPath, mode='w', encoding='utf-8') as f:
				json.dump(X, f)
			for theme_ in themes_:
				X[0].append(["", "", int(theme_), "O"])
			X0 = predict.predict(X, themes_)[0]
			difficulty = int(request.POST.get('difficulty'))
			program, problem, blanks_lst, answer_lst = vector2program.transform(X0, id, difficulty=difficulty)
			logger.info('\nOrigin file %d:\n%s' % (id, program))
			logger.info('\nProblem file %d:\n%s' % (id, problem))
			logger.info('\nBlanks %d:\n%s' % (id, blanks_lst))
			logger.info('\nAnswer %d:\n%s' % (id, answer_lst))
			with open(problem_file_path, mode='w') as f:
				f.write(problem)
			os.remove(origin_file_path)
			test_cases_obj = request.FILES.get('test-cases')
			if not os.path.exists("%s%s" % ('data/test_cases/', str(id))):
				os.mkdir("%s%s" % ('data/test_cases/', str(id)))
			else:
				print('directory already exists')
				logger.error('Directory -%s%s already exists' % ('data/test_cases/', str(id)))
				return False
			test_cases_path_rar = os.path.join('data/test_cases', str(id), str(id) + '.zip')
			test_cases_path = os.path.join('data/test_cases', str(id))
			f = open(test_cases_path_rar, mode="wb")
			for i in test_cases_obj.chunks():  # TODO(tdye): using coroutine?
				f.write(i)
			f.close()
			unzip_file(test_cases_path_rar, test_cases_path)
			os.remove(test_cases_path_rar)
			# update database

			try:
				db_problem = Problem(id=id, title=title, theme=themes, description=description, author=author,
				                     score=score, answer=json.dumps(answer_lst), blanks=json.dumps(blanks_lst))
				db_problem.save()
			except ValueError:
				print("Invalid parameters => (%d, %s, %s, %s, %s, ) while saving a problem!" % (
				id, title, themes, description, author))
				logger.error("Invalid parameters => (%d, %s, %s, %s, %s, ) while saving a problem!" % (
				id, title, themes, description, author))
			finally:
				request.session['program'] = program
				request.session['problem-id'] = id
				request.session['problem'] = problem
				request.session['answer'] = answer_lst
				return redirect('/generation')


def upload(request):
	return render(request, 'upload.html', {})


def generation(request):
	program = request.session['program']
	id = request.session['problem-id']
	problem = request.session['problem']
	answer = request.session['answer']
	return render(request, 'generation.html', {'program': program,
	                                           'problem': problem,
	                                           'id': id,
	                                           'answer': answer})


def admin(request):
	if request.method == 'GET':
		if request.GET.get('action') is None:
			return render(request, 'admin.html', {})
		elif request.GET.get('action') == 'logout':
			request.session['checkAdminSignin'] = False
			request.session['adminEmail'] = ''
			request.session['adminNickname'] = ''
			nextURL = request.GET.get('next')
			return redirect(nextURL)
		elif request.GET.get('action') == 'dashboard':
			if 'checkAdminSignin' not in request.session or not request.session['checkAdminSignin']:
				return redirect('/admin')
			studentNum = User.objects.all().count()
			teacherNum = Teacher.objects.all().count()
			problemNum = Teacher.objects.all().count()
			return render(request, 'dashboard.html', {'studentNum': studentNum,
			                                          'teacherNum': teacherNum,
			                                          'problemNum': problemNum})
		elif request.GET.get('action') == 'delete':
			role = request.GET.get('role')
			info = request.GET.get('info')
			if role == 'teacher':
				Teacher.objects.filter(email=info).delete()
				return HttpResponse(json.dumps({'status': 1, 'msg': 'Deleted Successfully.'}),
				                    content_type="application/json")
			elif role == 'student':
				User.objects.filter(email=info).delete()
				return HttpResponse(json.dumps({'status': 1, 'msg': 'Deleted Successfully.'}),
				                    content_type="application/json")
			elif role == 'problem':
				Problem.objects.filter(id=int(info)).delete()
				return HttpResponse(json.dumps({'status': 1, 'msg': 'Deleted Successfully.'}),
				                    content_type="application/json")
		elif request.GET.get('action') == 'lookAnswer':
			id = request.GET.get('id')
			problem = Problem.objects.filter(id=int(id)).values('answer')[0]
			answer = json.loads(problem['answer'])
			return HttpResponse(json.dumps({'status': 1, 'data': answer}),
			                    content_type="application/json")

	elif request.method == 'POST':
		if request.GET.get('action') == 'signin':
			postData = json.loads(request.body.decode())
			email = postData.get('email')
			password = postData.get('password')
			exist = Admin.objects.filter(email=email).exists()
			if exist:
				administrator = Admin.objects.all().filter(email=email)[0]
				if check_password(password, administrator.password):
					request.session['checkAdminSignin'] = True
					request.session['adminNickname'] = administrator.nickname
					request.session['adminEmail'] = administrator.email
					# status 1: login successful
					return HttpResponse(json.dumps({'status': 1, 'msg': 'Login successful'}),
					                    content_type="application/json")
				else:
					# status 0: Wrong password.
					return HttpResponse(json.dumps({'status': 0, 'msg': 'Wrong password.'}),
					                    content_type="application/json")
			else:
				# status -1: Account does not exist.
				return HttpResponse(json.dumps({'status': 0, 'msg': 'Account does not exist.'}),
				                    content_type="application/json")
		elif request.GET.get('action') == 'search':
			postData = json.loads(request.body.decode())
			query = postData.get('query')
			role = postData.get('role')
			way = postData.get('way')
			if role == 'teacher':
				if way == 'email':
					teachers = Teacher.objects.filter(email=query)
				elif way == 'nickname':
					teachers = Teacher.objects.filter(nickname__contains=query)
				data = []
				for item in teachers:
					data.append({'email': item.email, 'password': item.password, 'nickname': item.nickname})
				return HttpResponse(json.dumps({'status': 1, 'role': 'teacher', 'data': data}),
				                    content_type="application/json")
			elif role == 'student':
				if way == 'email':
					students = User.objects.filter(email=query)
				elif way == 'nickname':
					students = User.objects.filter(nickname__contains=query)
				data = []
				for item in students:
					data.append({'role': 'student', 'email': item.email, 'password': item.password, 'nickname': item.nickname, 'score': str(item.score)})
				return HttpResponse(json.dumps({'status': 1, 'role': 'student', 'data': data}),
				                    content_type="application/json")
			elif role == 'problem':
				if way == 'proId':
					problems = Problem.objects.filter(id=int(query))
				elif way == 'keyword':
					problems = Problem.objects.filter(title__contains=query)
				elif way == 'theme':
					problems = Problem.objects.filter(theme__contains=query)
				data = []
				for item in problems:
					data.append({'id': item.id, 'author': item.author, 'title': item.title, 'score': item.score, 'averageScore': str(item.averageScore)})
				return HttpResponse(json.dumps({'status': 1, 'role': 'problem', 'data': data}),
				                    content_type="application/json")