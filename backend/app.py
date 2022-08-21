import logging
from flask import Flask, jsonify, request, send_file
from flask_socketio import SocketIO
from flask_cors import CORS
import fileFunc, userInfo

app = Flask(__name__, template_folder='.')
CORS(app, resources=r'/*')
app.config["fd"] = {}
app.config["child_pid"] = {}

# cmd for win
app.config['cmd'] = 'bash'

socketio = SocketIO(app, cors_allowed_origins="*")

import python_debugger
import web_terminal

@app.route('/')
def hello_world():
    return 'Hello World!'

# 注册
@app.route('/api/signup', methods=["POST", "GET"])
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
@app.route('/api/login', methods = ["POST", "GET"])
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
@app.route('/api/logout/<username>', methods = ["POST"])
def logout(username):
    return "succeed logout"

# 重命名项目
@app.route('/api/renamepro/<username>', methods =["POST"])
def renamepro(username):
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
@app.route('/api/rename/<username>', methods =["POST"])
def rename(username):
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
@app.route('/api/deletepro/<username>', methods = ["POST"])
def deletepro(username):
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
@app.route('/api/delete/<username>', methods = ["POST"])
def delete(username):
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
@app.route('/api/mkpro/<username>', methods = ["POST"])
def mkpro(username):
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
@app.route('/api/mkdir/<username>', methods = ["POST"])
def mkdir(username):
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
@app.route('/api/touch/<username>', methods = ["POST"])
def touch(username):
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

# 保存文件
# 前端向后端上传文件
@app.route('/api/save/<username>', methods = ["POST"])
def save_file(username):
    src = request.get_json()['src']
    text = request.get_json()['text']
    if fileFunc.save(username + '/' + src, text):
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

@app.route('/api/upload/<username>/<projname>', methods = ["POST"])
def upload_file(username, projname):

    request_data = {
        'file': request.files.get('file'),
        'file_info': dict(request.form)
    }

    res = fileFunc.upload(f'./userfile/{username}/{projname}/', request_data)
    return jsonify(res)

# 加载文件
# 前端从后端下载文件
# 前端以get形式提供文件路径   xiaoming/file.txt
@app.route('/api/download/<username>', methods = ["GET"])
def download_file(username):
    src = request.args.get('src')
    flag, text = fileFunc.download(f'{username}/{src}')
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
@app.route('/api/getPro/<username>', methods = ["GET"])
def getPro(username):
    ls = userInfo.showpro(username)
    obj = {
        'flag': True,
        'message': None,
        'data': ls
    }
    return jsonify(obj)

# 提供某项目的文件树
@app.route('/api/getFileTree/<username>/<projectname>', methods = ["GET"])
def getFileTree(username, projectname):
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


# 移动文件（夹）
# 传入当前路径和指定路径
@app.route('/api/moveFile/<username>', methods = ["POST"])
def moveFile(username):
    src = request.get_json()['src']
    dst = request.get_json()['dst']
    if fileFunc.move(src, dst):
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
            'message': "Error file/folder name"
        }
        return jsonify(data)


# 上传文件
# 提供文件和目标存储文件夹
@app.route('/api/uploadFile/<username>', methods = ["GET", "POST"])
def uploadFile(username):
    fileObj = request.files.get('file')
    src = request.get_json()['src']
    filename = fileObj.filename
    upload_path = fileFunc.joinPath(src, filename)
    data = {
        'flag': False,
        'code': 500,
        'msg': "Failed to upload"
    }
    try:
        fileObj.save(upload_path)
        data.update({'flag': True, 'code': 200, 'msg': "Succeed uploading"})
    except FileNotFoundError as e:
        logging.log('error', e)
    return jsonify(data)


# 下载文件
@app.route('/api/downloadFile/<username>', methods = ["GET", "POST"])
def downloadFile(username):
    # 获取文件名
    # 从用户名一级开始
    file_name = request.json.get('fileName')
    flag, path = fileFunc.phyPath(file_name)
    if flag:
        # attachment_filename="down.txt", as_attachment=True 附件
        return send_file(path, attachment_filename=file_name, as_attachment=True)
    else:
        data = {
            "code": 404,
            "info": "file no found!"
        }
        return jsonify(data)


if __name__ == "__main__":
    socketio.run(app, port=5000, host='127.0.0.1')