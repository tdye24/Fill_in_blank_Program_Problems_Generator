# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/4/22 10:38
# @name:logfile
# @author:TDYe
import logging
import os.path
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

date = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_path = 'logs/'
log_name = log_path + date + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)

logger.addHandler(fh)

# logger.debug('this is a logger debug message')
# logger.info('this is a logger info message')
# logger.warning('this is a logger warning message')
# logger.error('this is a logger error message')
# logger.critical('this is a logger critical message')
