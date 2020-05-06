# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/4/5 11:08
# @name:tcp_socket_client_2
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


def compile_and_exe(submissionId_proId_th_: str, submissionId: str, proId: str, no_of_blank: str, i: str):
	compile_cmd = "g++ ../data/submissions/%s-normal-%s.cpp -o ../data/exe/%s-normal-%s.exe -O2 2>../data/compile_info/%s-normal-%s.txt" % (
	submissionId_proId_th_, i, submissionId_proId_th_, i, submissionId_proId_th_, i)
	compile_p = subprocess.Popen(compile_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	compile_p.communicate()
	if compile_p.returncode == 0:  # compile successfully
		# add include file #include<bits/stdc++.h> and IO redirect
		exe_cmd = "cd ../data/exe && %s-normal-%s.exe" % (submissionId_proId_th_, i)
		exe_p = subprocess.Popen(exe_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		exe_out, exe_err = exe_p.communicate()
		exe_p.wait()
		if exe_p.returncode == 0:  # exe successfully
			# out
			user_out_path = '../data/out/%s-%s.out' % (submissionId_proId_th_, i)
			answer_out_path = '../data/test_cases/%s/%s.out' % (proId, i)
			user_out = read_out(user_out_path)
			answer_out = read_out(answer_out_path)
			print('user output: ', user_out, ' answer output', answer_out)
			if user_out == answer_out:
				print('The no.%s blank of no.%s submission is right on no.%s test case' % (
					no_of_blank, submissionId, i))
				# logger.info('The no.%s blank of no.%s submission is right on no.%s test case' % (
				# no_of_blank, submissionId, i))
				return True
			else:  # TODO(tdye): add presentation error and other errors ...
				print('The no.%s blank of no.%s submission is wrong on no.%s test case' % (
					no_of_blank, submissionId, i))
				return False
	# TODO(tdye): fail to compile
	# cursor.execute(
	# 	"UPDATE dbmodel_submission SET judgeStatus = 0, score = " + str(20) + " where runId = " + str(run_id))
	# db.commit()
	# print('client 1 finished judging : %s' % run_id)


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
		print(data.decode())
		if data.decode() == 'get_status':
			if submission_queue.qsize() < 4:
				print('ready')
				client.send('ok'.encode())
			else:
				client.send('queue of judge client 1 is full'.encode())
		elif data.decode()[0: 5] == 'judge':
			client.send('gotten'.encode())
			submissionId_proId_th = data.decode()[6:]
			submission_queue.put(submissionId_proId_th)
		for _ in range(submission_queue.qsize()):
			submissionId_proId_th = submission_queue.get()
			submissionId = int(submissionId_proId_th.split('-')[0])
			proId = submissionId_proId_th.split('-')[1]
			no_of_blank = submissionId_proId_th.split('-')[2]
			cursor = db.cursor()
			generate_normal_files(submissionId_proId_th)
			test_cases_num = get_test_cases_num(proId)
			pool = multiprocessing.Pool()  # default 4
			resultList = []
			for i in range(test_cases_num):
				res = pool.apply_async(compile_and_exe,
				                       args=(submissionId_proId_th, submissionId, proId, no_of_blank, str(i + 1),))
				resultList.append(res)
			pool.close()
			pool.join()
			finalResult = True
			for res in resultList:
				finalResult = finalResult and res.get()
			print('client 1 finished judging no.%s blank of no.%s submission' % (no_of_blank, submissionId))
			# logger.info('client 1 finished judging no.%s blank of no.%s submission' % (no_of_blank, submissionId))
			if finalResult:
				cursor.execute(
					"SELECT answer, score from dbmodel_problem where id = " + proId)
				answerString, score = cursor.fetchone()
				addScore = score / len(json.loads(answerString))
				cursor.execute(
					"SELECT email from dbmodel_submission where submissionId = " + str(submissionId))
				email, = cursor.fetchone()
				cursor.execute(
					"UPDATE dbmodel_user SET dbmodel_user.score = dbmodel_user.score + " + str(
						addScore) + " where email = '" + str(email) + "'")
				db.commit()
				cursor.execute(
					"UPDATE dbmodel_submission SET dbmodel_submission.score = dbmodel_submission.score + " +
					str(addScore) + " where submissionId = " + str(submissionId))
				db.commit()
				# TODO(tdye): need to close the db?
			cursor.execute(
				"SELECT answer from dbmodel_problem where id = " + proId)
			totalBlanks = len(json.loads(cursor.fetchone()[0]))
			if totalBlanks == int(no_of_blank):
				# TODO(tdye): problem occurs when more than one judge client work concurrently
				# update average score and judge status
				cursor.execute(
					"UPDATE dbmodel_problem SET averageScore = "
					"(SELECT AVG(score) FROM dbmodel_submission WHERE proId = " + proId + ")	"
					" WHERE id = " + proId)
				cursor.execute(
					"UPDATE dbmodel_submission SET judgeStatus = 0 WHERE submissionId = " + str(submissionId))
				db.commit()
			cursor.close()
			sleep(1)
