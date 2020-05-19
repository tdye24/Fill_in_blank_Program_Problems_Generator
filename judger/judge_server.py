# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/4/5 10:09
# @name:tcp_socket
# @author:TDYe
import socket
import config
import threading
import MySQLdb
import queue
from time import sleep

queue_ = queue.Queue()
mutex = threading.Lock()

try:
	db = MySQLdb.connect(
		host=config.db_host,
		port=int(config.db_port),
		user=config.db_user,
		passwd=config.db_password,
		db=config.db_name,
		charset=config.db_charset)
except Exception as e:
	print(e, "Fail to connect database")
	exit(1)


def get_submission():
	global queue_, db
	cursor = db.cursor()
	while True:
		sleep(1)
		try:    # TODO(tdye): maybe needs a mutex lock
			cursor.execute(
				"SELECT submissionId, proId, answer from dbmodel_submission where judgeStatus = -2")
			data = cursor.fetchall()
			for item in data:
				blank_nums = len(item[2].split(','))
				for th in range(blank_nums):
					queue_.put('%s-%s-%s' % (str(item[0]), str(item[1]), str(th+1)))
				# -2 -> waiting
				cursor.execute("UPDATE dbmodel_submission SET judgeStatus = -1 WHERE submissionId = %d" % item[0])
			db.commit()
		except Exception as _e:
			print(_e)
			db.rollback()
	db.close()


def deal_client(newSocket: socket, addr):
	global queue_
	status = False
	while True:
		sleep(1)
		try:
			if status and not queue_.empty():
				submissionId_proId_th = queue_.get()
				print(submissionId_proId_th)
				newSocket.send(("judge|%s" % submissionId_proId_th).encode())
				data = newSocket.recv(1024)
				recv_data = data.decode()
				if recv_data == 'gotten':
					status = False
				else:
					queue_.put(submissionId_proId_th)
			else:
				newSocket.send('get_status'.encode())
				data = newSocket.recv(1024)
				recv_data = data.decode()
				if recv_data == "ok":
					status = True
				print(addr, status)
		except socket.error:
			newSocket.close()
		except Exception as e_:
			newSocket.close()
			print(e_)


HOST = '0.0.0.0'
PORT = 3000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(5)

t = threading.Thread(target=get_submission, args=())
t.setDaemon(True)
t.start()

while True:
	newSocket_, addr_ = server.accept()
	print("client [%s] is connected!" % str(addr_))
	client = threading.Thread(target=deal_client, args=(newSocket_, addr_))
	client.setDaemon(True)
	client.start()
