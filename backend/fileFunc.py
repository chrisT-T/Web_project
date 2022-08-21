#!/usr/bin/python
# -*- coding:utf-8 -*-
from fileinput import filename
import os, shutil
import re
from tokenize import String
from pathlib import Path
from typing import List
from urllib import request

# 文件根目录
FILE_PATH = "userfile/"

# 新建文件夹 参数从用户名层开始
def mkdir(path: String):
    path = os.path.join(FILE_PATH, path)
    folder = os.path.exists(path)
    # 文件夹不存在 新建
    if not folder:
        os.makedirs(path)
        return True
    else:
        return False

# 新建文件
def touch(path: String):
    path = os.path.join(FILE_PATH, path)
    if os.path.exists(path):
        return False
    else:
        open(path, 'w').close()
        return True



# 返回文件目录 参数从用户名层开始
def walk(path: String):
    path = os.path.join(FILE_PATH, path)
    p = Path(path)
    r = p.rglob('*')
    path_list = [str(i) for i in r] # there maybe some problems when cross platform
    return path_list

# 重命名文件(夹)
def rename(src: String, dst: String):
    src = os.path.join(FILE_PATH, src)
    dst = os.path.join(FILE_PATH, dst)
    if os.path.exists(src):
        try:
            os.rename(src, dst)
        except:
            return 2
        return 0
    else:
        print ("the file does not exist")
        return 1

# 删除文件夹
def deleteFolder(src: String):
    src = os.path.join(FILE_PATH, src)
    if os.path.exists(src):
        shutil.rmtree(src)
        return True
    else:
        print ("the directory does not exist")
        return False

# 删除文件
def deleteFile(src: String):
    src = os.path.join(FILE_PATH, src)
    if os.path.exists(src):
        os.remove(src)
        return True
    else:
        print ("the file does not exist")
        return False
    
def save(src: String, text: String):
    src = os.path.join(FILE_PATH, src)
    if os.path.exists(src):
        try:
            with open(src, 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except:
            print ("wrong file type")
            return False
    else:
        print ("the file does not exist")
        return False

def upload(src: String, request_data):

    file_content = request_data['file']
    file_name = request_data['file'].filename
    file_path = src + file_name
    if (os.path.exists(file_path)):
        return { 'msg': 'File exists' }
    else:
        file_content.save(file_path)
        return { 'msg': 'Upload Success' }

# 下载文件
def download(src: String):
    src = os.path.join(FILE_PATH, src)
    if os.path.exists(src):
        try:
            with open(src, 'r', encoding='utf-8') as f:
                data = f.read()
            return True, data
        except:
            print ("wrong file type")
            return False, None
    else:
        print ("the file does not exist")
        return False, None

# 输出指定路径一级目录
# 传入参数src必须是目录名 若是文件名直接返回错误
def walkone(inputSrc: String):
    src = os.path.join(FILE_PATH, inputSrc)
    route = inputSrc.split('/', 1)[1]
    if os.path.isfile(src):
        print ("shoule be a directory not a file")
        return False, []

    if os.path.exists(src):
        dirs = os.listdir(src)
        tmp_list = []
        for dir in dirs:
            path = os.path.join(src, dir)
            tmp_dict = {}
            tmp_dict['label'] = dir
            tmp_dict['route'] = route
            tmp_dict['isRoot'] = False
            tmp_dict['showInput'] = False
            # 是目录
            if os.path.isdir(path):
                tmp_dict['type'] = "folder"
            # 是文件
            elif os.path.isfile(path):
                tmp_dict['type'] = "file"
            tmp_list.append(tmp_dict)
        return True, tmp_list
    else:
        print ("the directory does not exist")
        return False, []

# 接收文件夹路径，返回该文件夹下所有文件和文件夹
# 返回一个列表，包括文件和文件夹
# 若是文件，则是一个字典，有属性label type route showInput isRoot children，其中children为空列表
# 若是文件夹，则是一个字典，有属性label type route showInput isRoot children，其中children一个结构类似于父列表的列表
def getData(src: String):
    # src从用户名一级开始
    flag, level0_list = walkone(src)
    if flag:
        for f in level0_list:
            if f['type'] == "file":
                f['children'] = []
            elif f['type'] == "folder":
                new_src = os.path.join(src, f['label'])
                _, f['children'] = getData(new_src)

        return True, level0_list
    return False, []


# 移动文件（夹）
def move(src: String, dst: String):
    src = os.path.join(FILE_PATH, src) 
    dst = os.path.join(FILE_PATH, dst) 

    # 目标路径下不能有重名
    basename = os.path.basename(src)
    # print (basename)
    if os.path.exists(os.path.join(dst, basename)):
        return False
    # 目标路径必须是文件夹
    if not os.path.isdir(dst):
        return False

    if os.path.exists(src) and os.path.exists(dst):
        shutil.move(src, dst)
        return True
    return False

# 将相对路径拼接为后端实际路径
def joinPath(src: String, filename:String):
    path = os.path.join(FILE_PATH, src, filename)
    return path

# 返回文件在后端的实际路径
def phyPath(path: String):
    path = os.path.join(FILE_PATH, path)
    if os.path.exists(path):
        return True, path
    else:
        return False, None
