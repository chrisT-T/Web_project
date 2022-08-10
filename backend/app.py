from distutils.log import error
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import fileFunc, userInfo

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route('/')
def hello_world():
    return 'Hello World!'



# 全局变量 记录当前用户文件夹
folder_list = []

# 注册
@app.route('/signup', methods=["POST", "GET"])
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
        userInfo.setCurUser(user)
        fileFunc.mkdir(user)
        folder_list.clear()

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
@app.route('/login', methods = ["POST", "GET"])
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
        data = {
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
@app.route('/logout/<username>', methods = ["POST"])
def logout(username):
    if username != userInfo.currentUser():
        raise error

    userInfo.setCurUser('')
    folder_list.clear()
    return "succeed logout"

# 重命名项目
@app.route('/renamepro/<username>', methods =["POST"])
def renamepro(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    dst = request.get_json()['dst']
    result = fileFunc.rename(src, dst)
    if result == 0:
        userInfo.renamepro(src, dst)
        data = {
            'flag': True,
            'message': None
        }
        return jsonify(data)
    elif result == 1:
        data = {
            'flag': False,
            'message': "The file/folder to rename does not exist"
        }
        return jsonify(data)
    elif result == 2:
        data = {
            'flag': False,
            'message': "The name already used"
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "unexpected result"
        }
        return jsonify(data)

# 重命名文件（夹）
# 前端json形式传入 
# 路径从用户名开始   xiaoming/...  
@app.route('/rename/<username>', methods =["POST"])
def rename(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    dst = request.get_json()['dst']
    print(src, dst)
    result = fileFunc.rename(src, dst)
    if result == 0:
        data = {
            'flag': True,
            'message': None
        }
        return jsonify(data)
    elif result == 1:
        data = {
            'flag': False,
            'message': "The file/folder to rename does not exist"
        }
        return jsonify(data)
    elif result == 2:
        data = {
            'flag': False,
            'message': "The name already used"
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "unexpected result"
        }
        return jsonify(data)

# 删除项目
@app.route('/deletepro/<username>', methods = ["POST"])
def deletepro(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    if fileFunc.deleteFolder(src):
        userInfo.deletepro(src)
        data = {
            'flag': True,
            'message': None
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "The project does not exist"
        }
        return jsonify(data)
    return jsonify(data)

# 删除文件(夹)
@app.route('/delete/<username>', methods = ["POST"])
def delete(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    type = request.get_json()['type']
    if type == "folder":
        if fileFunc.deleteFolder(src):
            data = {
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

#新建项目
@app.route('/mkpro/<username>', methods = ["POST"])
def mkpro(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    language = request.get_json()['type']
    if fileFunc.mkdir(src):
        t = userInfo.saveProject(src, language)
        data = {
            'flag': True,
            'message': None,
            'lastupdate': t
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "Duplicate foldername"
        }
        return jsonify(data)

# 新建文件夹
@app.route('/mkdir/<username>', methods = ["POST"])
def mkdir(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    if fileFunc.mkdir(src):
        data = {
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
@app.route('/touch/<username>', methods = ["POST"])
def touch(username):
    if username != userInfo.currentUser():
        raise error

    src = request.get_json()['src']
    print(src)
    if fileFunc.touch(src):
        data = {
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
@app.route('/upload/<username>', methods = ["POST"])
def upload_file(username):
    src = request.get_json()['src']
    text = request.get_json()['text']
    if fileFunc.upload(src, text):
        data = {
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
@app.route('/download/<username>', methods = ["GET"])
def download_file(username):
    src = request.get_json()['src']
    flag, text = fileFunc.download(src)
    if flag:
        data = {
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

# 提供项目列表
@app.route('/getPro/<username>', methods = ["GET"])
def getPro(username):
    if username != userInfo.currentUser():
        raise error
    ls = userInfo.showpro(username)
    obj = {
        'flag': True,
        'message': None,
        'data': ls
    }
    return jsonify(obj)

# 提供某项目的文件树
@app.route('/getFileTree/<username>/<projectname>', methods = ["GET"])
def getFileTree(username, projectname):
    if username != userInfo.currentUser():
        raise error
    flag, fileTree = fileFunc.getData(username + '/' + projectname)
    if flag:
        data = {
            'flag': True,
            'message': None,
            'fileTree': fileTree
        }
        return jsonify(data)
    else:
        data = {
            'flag': False,
            'message': "cannot get the fileTree",
            'fileTree': []
        }
        return jsonify(data)


if __name__ == "__main__":
    app.run(port=5000, host='127.0.0.1')