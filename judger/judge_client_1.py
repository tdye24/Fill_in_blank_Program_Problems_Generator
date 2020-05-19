# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/4/5 15:01
# @name:tcp_socket_client_1
# @author:TDYe
import json
import socket
import subprocess
import queue
import MySQLdb
import config
import multiprocessing
from tools import get_test_cases_num, generate_normal_files, read_out
from time import sleep


# from logfile import logger


def compile_and_exe(submissionId: str, proId: str, noBlank: str, noCase):
	compile_cmd = "g++ ../data/submissions/%s-%s-%s-normal-%s.cpp " \
	              "-o ../data/exe/%s-%s-%s-normal-%s.exe " \
	              "-O2 2>../data/compile_info/%s-%s-%s-normal-%s.txt" \
	              % (submissionId, proId, noBlank, noCase,
	                 submissionId, proId, noBlank, noCase,
	                 submissionId, proId, noBlank, noCase)
	compile_p = subprocess.Popen(compile_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	compile_p.communicate()
	if compile_p.returncode == 0:  # compile successfully
		# add include file #include<bits/stdc++.h> and IO redirect
		exe_cmd = "cd ../data/exe && %s-%s-%s-normal-%s.exe" % (submissionId, proId, noBlank, noCase)
		exe_p = subprocess.Popen(exe_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		exe_out, exe_err = exe_p.communicate()
		exe_p.wait()
		if exe_p.returncode == 0:  # exe successfully
			# out
			user_out_path = '../data/out/%s-%s-%s-%s.out' % (submissionId, proId, noBlank, noCase)
			answer_out_path = '../data/test_cases/%s/%s.out' % (proId, noCase)
			user_out = read_out(user_out_path)
			answer_out = read_out(answer_out_path)
			print('user output: ', user_out, ' answer output', answer_out)
			if user_out == answer_out:
				print('The no.%s blank of no.%s submission is right on no.%s test case' % (
					noBlank, submissionId, noCase))
				# logger.info('The no.%s blank of no.%s submission is right on no.%s test case' % (
				# no_of_blank, submissionId, i))
				return True
			else:  # TODO(tdye): add presentation error and other errors ...
				print('The no.%s blank of no.%s submission is wrong on no.%s test case' % (
					noBlank, submissionId, noCase))
				return False
	# TODO(tdye): fail to compile
	# cursor.execute(
	# 	"UPDATE dbmodel_submission SET judgeStatus = 0, score = " + str(20) + " where runId = " + str(run_id))
	# db.commit()
	# print('client 2 finished judging : %s' % run_id)


if __name__ == '__main__':
	try:
		db = MySQLdb.connect(
			host=config.db_host,
			port=int(config.db_port),
			user=config.db_user,
			passwd=config.db_password,
			db=config.db_name,
			charset=config.db_charset)
	except Exception as e:
		print("fail to connect database")
		print(e)
		exit(1)

	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	HOST = "127.0.0.1"
	PORT = 3000
	client.connect((HOST, PORT))

	print("server ip：%s, server port：%s" % (HOST, str(PORT)))
	submission_queue = queue.Queue(5)
	while True:
		data = client.recv(1024)
		print('server:' + data.decode())
		if data.decode() == 'get_status':
			if submission_queue.qsize() < 4:
				print('client: ready')
				client.send('ok'.encode())
			else:
				client.send('queue of judge client 1 is full'.encode())
		elif data.decode()[0: 5] == 'judge':
			client.send('gotten'.encode())
			submissionId_proId = data.decode()[6:]
			submission_queue.put(submissionId_proId)
		for _ in range(submission_queue.qsize()):
			submissionId_proId = submission_queue.get()
			submissionId = int(submissionId_proId.split('-')[0])
			proId = submissionId_proId.split('-')[1]
			cursor = db.cursor()
			blankNums = 0
			try:
				cursor.execute('SELECT answer from dbmodel_problem where id = ' + str(proId))
				answer, = cursor.fetchone()
				blankNums = len(json.loads(answer))
				for i in range(blankNums):
					generate_normal_files("%s-%s" % (submissionId_proId, str(i+1)))
			except Exception as e:
				print(e, "Exception occurs when generating normal files.")
			for i in range(blankNums):
				pool = multiprocessing.Pool()  # default 4
				resultList = []
				test_cases_num = get_test_cases_num(proId)
				for j in range(test_cases_num):
					res = pool.apply_async(compile_and_exe,
					                       args=(str(submissionId), str(proId), str(i+1), str(j+1),))
					resultList.append(res)
				pool.close()
				pool.join()
				finalResult = True
				for res in resultList:
					finalResult = finalResult and res.get()
				print('client 1 finished judging no.%d blank of no.%s submission' % (i+1, submissionId))
				# logger.info('client 1 finished judging no.%s blank of no.%s submission' % (no_of_blank, submissionId))
				if finalResult:
					try:
						cursor.execute(
							"SELECT answer, score from dbmodel_problem where id = " + proId)
						answerString, score = cursor.fetchone()
						addScore = score / len(json.loads(answerString))
					except Exception as e:
						print(e, "Exception occurs when calculating addScore.")
					try:
						cursor.execute(
							"SELECT email from dbmodel_submission where submissionId = " + str(submissionId))
						email, = cursor.fetchone()
					except Exception as e:
						print(e, "Exception occurs when fetching email of specified submission id.")
					try:
						cursor.execute(
							"UPDATE dbmodel_user SET dbmodel_user.score = dbmodel_user.score + " + str(
								addScore) + " where email = '" + str(email) + "'")
						db.commit()
					except Exception as e:
						print(e, "Exception occurs when updating user's score.")
					try:
						cursor.execute(
							"UPDATE dbmodel_submission SET dbmodel_submission.score = dbmodel_submission.score + " +
							str(addScore) + " where submissionId = " + str(submissionId))
						db.commit()
					except Exception as e:
						print(e, "Exception occurs when updating submission's score.")
					# TODO(tdye): need to close the db?
			# try:
			# 	cursor.execute(
			# 		"SELECT answer from dbmodel_problem where id = " + proId)
			# 	totalBlanks = len(json.loads(cursor.fetchone()[0]))
			# except Exception as e:
			# 	print(e, "Exception occurs when fetching the total num of blanks.")
			# if totalBlanks == int(no_of_blank):
				# TODO(tdye): problem occurs when more than one judge client work concurrently
				# update average score and judge status
			try:
				cursor.execute(
					"UPDATE dbmodel_problem SET averageScore = "
					"(SELECT AVG(score) FROM dbmodel_submission WHERE proId = " + proId + ")	"
					" WHERE id = " + proId)
				cursor.execute(
					"UPDATE dbmodel_submission SET judgeStatus = 0 WHERE submissionId = " + str(submissionId))
				db.commit()
			except Exception as e:
				print(e, "Exception occurs when updating judge status and average score.")
			cursor.close()
