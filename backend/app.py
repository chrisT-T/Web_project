from flask import Flask, jsonify 
from flask_cors import CORS
from importlib_metadata import method_cache
from requests import RequestException, request
from . import fileFunc, userInfo

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/')
def hello_world():
    return 'Hello World!'

# 前端请求登陆 发送请求 
# 参数：用户名userName、密码userPassword 
# 返回当前用户的文件目录
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
    # 合法则为其创建文件夹 后续可改成注册时创建文件夹
    # 否则重新输入用户名密码
    if userInfo.isValid(user, password):
        fileFunc.mkdir(user)
        path_list = fileFunc.walk(user)
        return jsonify({'path_list': path_list})
    else:
        return "用户名密码错误"

# 重命名文件（夹）
# 前端json形式传入 
# 路径从用户名开始   xiaoming/...
@app.route('/rename/<username>', method ="POST")
def rename(username):
    src = request.get_json()['src']
    dst = request.get_json()['dst']
    if fileFunc.rename(src, dst):
        path_list = fileFunc.walk(username)
        return jsonify({'path_list': path_list})
    else:
        return "文件不存在"

# 删除文件
@app.route('./delete/<username>', method = "POST")
def delete(username):
    src = request.get_json()['src']
    type = request.get_json()['type']
    if type == "folder":
        pass
    elif type == "file":
        pass
    else: 
        return "error input"


# 前端向后端上传文件
@app.route('/upload', method = "POST")
def upload_file():
    pass

# 前端从后端下载文件
# 前端以get形式提供文件路径   xiaoming/file.txt
@app.route('/download/<filename>', method = "GET")
def download_file(filename):
    pass

if __name__ == "__main__":
    app.run(debug=True)