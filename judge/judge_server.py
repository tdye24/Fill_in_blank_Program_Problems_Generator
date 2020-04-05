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

queue = queue.Queue()
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
	print("fail to connect database")
	print(e)
	exit(1)


def get_submission():
	global queue, mutex, db
	cursor = db.cursor()
	while True:
		sleep(1)
		if mutex.acquire():
			cursor.execute(
				"SELECT * from dbmodel_submission where judgeStatus = -1")
			data = cursor.fetchall()
			try:
				for item in data:
					queue.put(item[0])
					# -2 -> waiting
					cursor.execute("UPDATE dbmodel_submission SET judgeStatus = -2 WHERE runId = %d" % item[0])
				db.commit()
			except:
				db.rollback()
			mutex.release()
	db.close()


def deal_client(newSocket: socket, addr):
	global mutex, queue
	status = False
	while True:
		sleep(2)
		try:
			if status and not queue.empty():
				mutex.acquire()
				runId = queue.get()
				mutex.release()
				print(runId)
				newSocket.send(("judge|%d" % runId).encode())
				data = newSocket.recv(1024)
				recv_data = data.decode()
				print(recv_data)
				status = False
			else:
				newSocket.send('get_status'.encode())
				data = newSocket.recv(1024)
				recv_data = data.decode()
				if recv_data == "ok":
					status = True
				print(addr, status)
		except socket.error:
			newSocket.close()
		except:
			newSocket.close()
			print('error!')


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
