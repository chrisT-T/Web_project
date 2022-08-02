from distutils.log import error
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from . import fileFunc, userInfo

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/')
def hello_world():
    return 'Hello World!'



# 全局变量 记录当前用户文件夹
folder_list = []



# 注册
@app.route('/signup', method = ["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form['userName']
        password = request.form['userPassword']
    else:
        user = request.args.get('userName')
        password = request.args.get('userPassword')
    if userInfo.isValid(user):
        # 成功注册
        userInfo.createNewUser(user, password)
        fileFunc.mkdir(user)
        data = {
            'flag': True,
            'message': None,
        }
        return jsonify(data)
    else:
        # 用户名已被使用
        data = {
            'flag': False,
            'message': "Duplicate username",
        }
        return jsonify(data)


# 前端请求登陆 发送请求 
# 可以不注销上个账号直接登陆 上个账号会被挤掉
# 参数：用户名userName、密码userPassword 
'''
userfile\xiaoming\dir.txt
userfile\xiaoming\test1.txt
userfile\xiaoming\testdir
userfile\xiaoming\testdir\a.txt
'''
@app.route('/login', method = ["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form['userName']
        password = request.form['userPassword']
    else:
        user = request.args.get('userName')
        password = request.args.get('userPassword')
    # 判断用户名 密码的合法性
    # 否则重新输入用户名密码
    if userInfo.isCorrect(user, password):  
        userInfo.setCurUser(user)  
        folder_list.clear()
        # 成功登陆  
        flag, path_list = fileFunc.walkone(user)
        data = {
            'path_list': path_list,
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "Wrong user name or password"
        }
        return jsonify(data)


# 注销
@app.route('/logout/<username>', method = "POST")
def logout(username):
    if username != userInfo.currentUser():
        raise error

    userInfo.setCurUser('')
    folder_list.clear()
    return "succeed logout"

# 重命名文件（夹）
# 前端json形式传入 
# 路径从用户名开始   xiaoming/...  
@app.route('/rename/<username>', method ="POST")
def rename(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    dst = request.get_json()['dst']
    if fileFunc.rename(src, dst):
        path_list = fileFunc.walk(username)
        data = {
            'path_list': path_list,
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "The file/folder does not exist"
        }
        return jsonify(data)

# 删除文件(夹)
@app.route('./delete/<username>', method = "POST")
def delete(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    type = request.get_json()['type']
    if type == "folder":
        if fileFunc.deleteFolder(src):
            path_list = fileFunc.walk(username)
            data = {
                'path_list': path_list,
                'flag': True,
                'message': None
            }
            return jsonify(data)
        else:
            data = {
                'flag': False,
                'message': "The folder does not exist"
            }
            return jsonify(data)
    elif type == "file":
        if fileFunc.deleteFile(src):
            path_list = fileFunc.walk(username)
            data = {
                'path_list': path_list,
                'flag': True,
                'message': None
            }
            return jsonify(data)
        else:
            data = {
                'flag': False,
                'message': "The file does not exist"
            }
            return jsonify(data)
    else: 
        data = {
                'flag': False,
                'message': "No such type"
            }
        return jsonify(data)


# 新建文件夹
@app.route('./mkdir/<username>', method = "POST")
def mkdir(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    if fileFunc.mkdir(src):
        path_list = fileFunc.walk(username)
        data = {
            'path_list': path_list,
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "Duplicate foldername"
        }
        return jsonify(data)

# 新建文件
@app.route('./touch/<username>', method = "POST")
def touch(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    if fileFunc.touch(src):
        path_list = fileFunc.walk(username)
        data = {
            'path_list': path_list,
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "Duplicate filename"
        }
        return jsonify(data)

# 前端向后端上传文件
@app.route('/upload/<username>', method = "POST")
def upload_file(username):
    src = request.get_json()['src']
    text = request.get_json()['text']
    if fileFunc.upload(src, text):
        path_list = fileFunc.walk(username)
        data = {
            'path_list': path_list,
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "The file does not exist"
        }
        return jsonify(data)

# 前端从后端下载文件
# 前端以get形式提供文件路径   xiaoming/file.txt
@app.route('/download/<username>', method = "GET")
def download_file(username):
    src = request.get_json()['src']
    flag, text = fileFunc.download(src)
    if flag:
        path_list = fileFunc.walk(username)
        data = {
            'path_list': path_list,
            'text': text,
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "The file does not exist"
        }
        return jsonify(data)
        

# 返回前端当前路径一级目录
# 传入参数必须是文件夹路径
@app.route('/show/<username>', method = "POST")
def show(username):
    if username != userInfo.currentUser():
        raise error
    
    src = request.get_json()['src']
    flag, outputList = fileFunc.walkone(src)
    if flag:
        data = {
            'filelist': outputList,
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "Path error"
        }
        return jsonify(data)


# 获取最外层tree数据结构
@app.route('/getTreeData/<username>', method = "GET")
def getTreeData(username):
    if username != userInfo.currentUser():
        raise error

    flag, path_list = fileFunc.getTreeData(username, folder_list)
    if flag:
        obj = {
            'code': 0,
            'data': path_list,
            'flag': True,
            'message': None
        }
    else:
        obj = {
            'flag': False,
            'message': "Failed to get"
        }
    return jsonify(obj)


# 根据id查询对应层级tree数据
@app.route('/getTreeChildData/<username>', method = "GET")
def getTreeChildData(username):
    if username != userInfo.currentUser():
        raise error

    id = request.args.get('id')
    flag, path_list = fileFunc.getTreeChildData(id, folder_list)
    if flag:
        obj = {
            'code': 0,
            'data': path_list,
            'flag': True,
            'message': None
        }
    else:
        obj = {
            'flag': False,
            'message': "Failed to get"
        }
    return jsonify(obj)


# 接收文件夹路径，返回该文件夹下所有文件和文件夹
@app.route('/getData/<username>', method = "POST")
def getData(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    flag, path_list = fileFunc.getData(src)
    if flag:
        data = {
            'filelist': path_list,
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "Path error"
        }
        return jsonify(data)



if __name__ == "__main__":
    app.run(debug=True)