#!/usr/bin/python
# -*- coding:utf-8 -*-
from msilib.schema import File
import os, shutil
from tokenize import String
from pathlib import Path

# 文件根目录
FILE_PATH = "userfile/"

# 新建文件夹 参数从用户名层开始
def mkdir(path: String):
    path = os.path.join(FILE_PATH, path)
    folder = os.path.exists(path)
    # 文件夹不存在 新建
    if not folder:
        os.makedirs(path)
        # open(path+"dir.txt", 'w').close()
        print ("create new folder: "+path)
        print ("----------------------")
    else:
        print (path + " the folder has existed")
        print ("----------------------")
    
# 返回文件目录 参数从用户名层开始
def walk(path: String):
    path = os.path.join(FILE_PATH, path)
    p = Path(path)
    r = p.rglob('*')
    path_list = []
    for i in r:
        print (i)
        # <class 'pathlib.WindowsPath'>
        path_list.append(str(i))
    return path_list

# 重命名文件(夹)
def rename(src: String, dst: String):
    src = os.path.join(FILE_PATH, src)
    dst = os.path.join(FILE_PATH, dst)
    if os.path.exists(src):
        os.rename(src, dst)
        return True
    else:
        print ("文件不存在")
        return False

# 删除文件(夹)
def deleteFolder(src: String):
    src = os.path.join(FILE_PATH, src)
    try:
        shutil.rmtree(src)
    except OSError as e:
        print("Error: %s - %s." % (e.filename, e.strerror)) 


# mkdir("xiaoming/")
# walk('')
# rename("xiaoming", "xiaohong")
# walk("xiaoming/")
# mkdir("xiaolan")
deleteFolder("xiaoming")