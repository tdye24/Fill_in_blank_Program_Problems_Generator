# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/4/5 10:15
# @name:tcp_socket_client
# @author:TDYe
import socket
import subprocess
import threading
import queue
import MySQLdb
import config
from tools import get_test_cases_num, generate_normal_files
from time import sleep


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
submission_queue = queue.Queue(5)
# result_queue = queue.Queue()
client.connect((HOST, PORT))
print("server ip：%s, server port：%s" % (HOST, str(PORT)))


def judge(submissionId_proId_th_: str):
	global db
	submissionId = int(submissionId_proId_th_.split('-')[0])
	proId = submissionId_proId_th_.split('-')[1]
	no_of_blank = submissionId_proId_th_.split('-')[2]
	cursor_ = db.cursor()
	generate_normal_files(submissionId_proId_th_)
	test_cases_num = get_test_cases_num(proId)
	for i in range(test_cases_num):
		compile_cmd = "g++ ../data/submissions/%s-normal-%s.cpp -o ../data/exe/%s-normal-%s.exe -O2 2>../data/compile_info/%s-normal-%s.txt" % (submissionId_proId_th_, str(i+1), submissionId_proId_th_, str(i+1), submissionId_proId_th_, str(i+1))
		compile_p = subprocess.Popen(compile_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		compile_out, compile_err = compile_p.communicate()
		compile_p.wait()
		if compile_p.returncode == 0:   # compile successfully
			# add include file #include<bits/stdc++.h> and IO redirect
			exe_cmd = "cd ../data/exe && %s-normal-%s.exe" % (submissionId_proId_th_, str(i+1))
			exe_p = subprocess.Popen(exe_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			exe_out, exe_err = exe_p.communicate()
			exe_p.wait()
			if exe_p.returncode == 0:   # exe successfully
				# out
				user_out_path = '../data/out/%s-%s.out' % (submissionId_proId_th_, str(i+1))
				answer_out_path = '../data/test_cases/%s/%s.out' % (proId, str(i+1))
				with open(user_out_path, 'r') as f:
					print('user out')
					user_out = ''
					for line in f.readlines():
						print(line)
						user_out += line
				with open(answer_out_path, 'r') as f:
					print('answer out')
					answer_out = ''
					for line in f.readlines():
						print(line)
						answer_out += line
				if user_out == answer_out:
					print('The no.%s blank of no.%s submission is right on no.%s test case' % (no_of_blank, submissionId, str(i+1)))
				else:   # TODO(tdye): add presentation error and other errors ...
					print('The no.%s blank of no.%s submission is wrong on no.%s test case' % (no_of_blank, submissionId, str(i+1)))
		else:
			pass
			# TODO(tdye): fail to compile
			# cursor.execute(
			# 	"UPDATE dbmodel_submission SET judgeStatus = 0, score = " + str(20) + " where runId = " + str(run_id))
			# db.commit()
			# print('client 1 finished judging : %s' % run_id)
	print('client 1 finished judging no.%s blank of no.%s submission' % (no_of_blank, submissionId))


while True:
	data = client.recv(1024)
	print(data.decode())
	if data.decode() == 'get_status':
		if submission_queue.qsize() < 5:
			print('ready')
			client.send('ok'.encode())
		else:
			client.send('queue of judge client 1 is full'.encode())
	elif data.decode()[0: 5] == 'judge':
		client.send('gotten'.encode())
		submissionId_proId_th = data.decode()[6:]
		submission_queue.put(submissionId_proId_th)
	for _ in range(submission_queue.qsize()):
		submissionId_proId_th =submission_queue.get()
		t = threading.Thread(target=judge, args=(submissionId_proId_th, ))
		t.setDaemon(True)
		t.start()
		t.join()
		cursor = db.cursor()
		try:    # TODO(tdye):   update table many times
			run_id = int(submissionId_proId_th.split('-')[0])
			cursor.execute(
				"UPDATE dbmodel_submission SET judgeStatus = 0 where proId = " + str(run_id))
			db.commit()
		except Exception as e_:
			print(e_)
			db.rollback()
		#   db.close()
		# TODO(tdye): need to close the db?
		sleep(1)
