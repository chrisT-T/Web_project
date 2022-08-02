#!/usr/bin/python
# -*- coding:utf-8 -*-
import os, shutil
import re
from tokenize import String
from pathlib import Path
from typing import List

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
    open(path, 'w').close()



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
        os.rename(src, dst)
        return True
    else:
        print ("the file does not exist")
        return False

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
    

# 问题： 目前只支持文本文件
# 上传文件
def upload(src: String, text: String):
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

# 输出指定路径一级目录 字典列表
# 传入参数src必须是目录名 若是文件名直接返回错误
def walkone(src: String):
    src = os.path.join(FILE_PATH, src)
    if os.path.isfile(src):
        print ("shoule be a directory not a file")
        return False, []

    if os.path.exists(src):
        dirs = os.listdir(src)
        tmp_list = []
        for dir in dirs:
            path = os.path.join(src, dir)
            tmp_dict = {}
            tmp_dict['name'] = dir
            # 是目录
            if os.path.isdir(path):
                tmp_dict['type'] = "folder"
            # 是文件
            elif os.path.isfile(path):
                tmp_dict['type'] = "file"
            tmp_list.append(tmp_dict)
        # print (tmp_list)
        return True, tmp_list
    else:
        print ("the directory does not exist")
        return False, []



# 获取最外层tree数据结构
def getTreeData(username: String, folder_list: List):
    tmp_list = []
    flag, level0_list = walkone(username)
    if not flag:
        return False
    i = 1
    for f in level0_list:
        tmp_dict = {}
        tmp_dict['name'] = f['name']
        tmp_dict['id'] = str(i) * 3
        tmp_dict['path'] = os.path.join(username, tmp_dict['name'])
        if f['type'] == 'file':
            tmp_dict['isLeaf'] = True
        elif f['type'] == 'folder':
            tmp_dict['isLeaf'] = False
            folder_list.append(tmp_dict)  # 将文件夹加入文件夹列表

        tmp_list.append(tmp_dict)
        i += 1
    return True, tmp_list


# 根据id查询对应层级tree数据
def getTreeChildData(id: String, folder_list: List):
    tmp_list = []
    for folder in folder_list:
        # 找到目标文件夹
        if folder['id'] == id:
            
            flag, level_list = walkone(folder['path'])
            if not flag:
                return False

            i = 1
            for f in level_list:
                tmp_dict = {}
                tmp_dict['name'] = f['name']
                tmp_dict['id'] = id + '-' + str(i) * 3
                tmp_dict['path'] = os.path.join(folder['path'], tmp_dict['name'])
                if f['type'] == 'file':
                    tmp_dict['isLeaf'] = True
                elif f['type'] == 'folder':
                    tmp_dict['isLeaf'] = False
                    folder_list.append(tmp_dict)  # 将文件夹加入文件夹列表

                tmp_list.append(tmp_dict)
                i += 1
    return True, tmp_list


# 接收文件夹路径，返回该文件夹下所有文件和文件夹
# 返回一个列表，包括文件和文件夹
# 若是文件，则是一个字典，有属性name type children，其中children为空列表
# 若是文件夹，则是一个字典，有属性name type children，其中children一个结构类似于父列表的列表
def getData(src: String):
    # src从用户名一级开始
    flag, level0_list = walkone(src)
    if flag:
        for f in level0_list:
            if f['type'] == "file":
                f['children'] = []
            elif f['type'] == "folder":
                new_src = os.path.join(src, f['name'])
                f['children'] = getData(new_src)

        return True, level0_list
    return False, []

# walkone("xiaolan/test1")
# l = getData("xiaolan")
# print (l)