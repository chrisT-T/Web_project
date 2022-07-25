from flask import Flask 
from flask_cors import CORS
from importlib_metadata import method_cache
from requests import request
from . import fileFunc

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/')
def hello_world():
    return 'Hello World!'

# 前端请求登陆 发送请求 
# 参数：用户名userName、密码userPassword 
# 返回当前用户的文件目录
@app.route('/login', method = ["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form['userName']
        password = request.form['userPassword']
    else:
        user = request.args.get('userName')
        password = request.args.get('userPassword')


# 前端向后端上传文件
@app.route('/upload', method = "POST")
def upload_file():
    pass

if __name__ == "__main__":
    app.run(debug=True)