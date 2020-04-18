# ！usr/bin/python
# -*- coding:utf-8 -*-#
# @date:2020/4/19 0:50
# @name:tools
# @author:TDYe
import zipfile


def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not a zip file')
