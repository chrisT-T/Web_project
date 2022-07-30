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
        # open(path+"dir.txt", 'w').close()
        print ("create new folder: "+path)
        print ("----------------------")
        return True
    else:
        print (path + " the folder has existed")
        print ("----------------------")
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

# 删除文件夹
def deleteFolder(src: String):
    src = os.path.join(FILE_PATH, src)
    if os.path.exists(src):
        shutil.rmtree(src)
        return True
    else:
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
            file = open(src, 'w', encoding='utf-8')
            file.write(text)
            file.close()
            return True
        except:
            print ("文件形式错误")
            return False
    else:
        print ("文件不存在")
        return False

# 下载文件
def download(src: String):
    src = os.path.join(FILE_PATH, src)
    if os.path.exists(src):
        try:
            file = open(src, 'r')
            data = file.read()
            file.close()
            print(data)
            return True, data
        except:
            print ("文件形式错误")
            return False, None
    else:
        print ("文件不存在")
        return False, None

# 输出指定路径一级目录
# 传入参数src必须是目录名 若是文件名直接返回错误
def walkone(src: String):
    src = os.path.join(FILE_PATH, src)
    if os.path.isfile(src):
        print ("格式错误")
        return False

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
        print ("路径错误")
        return False, None



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
        if f['type'] == 'file':
            tmp_dict['isLeaf'] = True
        elif f['type'] == 'folder':
            tmp_dict['isLeaf'] = False
            tmp_dict['path'] = os.path.join(username, tmp_dict['name'])
            folder_list.append(tmp_dict)  # 将文件夹加入文件夹列表

        tmp_list.append(tmp_dict)
        i += 1

    # print (tmp_list)
    return True, tmp_list


# 根据id查询对应层级tree数据
def getTreeChildData(id: String, folder_list: List):
    # print (folder_list)
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
                if f['type'] == 'file':
                    tmp_dict['isLeaf'] = True
                elif f['type'] == 'folder':
                    tmp_dict['isLeaf'] = False
                    tmp_dict['path'] = os.path.join(folder['path'], tmp_dict['name'])
                    folder_list.append(tmp_dict)  # 将文件夹加入文件夹列表

                tmp_list.append(tmp_dict)
                i += 1

    # print (tmp_list)
    return True, tmp_list





# mkdir("xiaoming/")
# walk('')
# rename("xiaoming", "xiaolan")
# walk("xiaoming/")
# mkdir("xiaolan")
# deleteFolder("xiaohong")
# touch('xiaolan/b.py')
# upload('xiaolan/b.py', 
# """
# def myhelloworld():
#     # 成功
#     print ("hello world")

# myhelloworld()
# """)
# download("xiaolan/b.py")
# walkone("xiaolan/b.py")
# l = []
# getTreeData("xiaolan", l)
# getTreeChildData("444", l)
# getTreeChildData("444-333", l)