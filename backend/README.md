## 后端接口

+ 登陆
  + 接收前端的用户名和密码，将该用户的文件目录返还
  + 需要注册页面和对应接口，同时登陆时判断用户名密码是否正确，暂时可在首次登陆时创建账户
+ 注销
+ 文件传输
  + 新建文件/项目
  + 保存文件/项目
  + 打开文件/项目
  + 删除
  + 重命名



> 文件上传以表单形式  必须要设置好请求头
>
> ```html
> <form action="http://localhost:7787/files" enctype="multipart/form-data" method="POST">
>   <input name="file" type="file" id="file">
>   <input type="submit" value="提交">
> </form>
> ```



## 问题

+ 需要二进制形式传输文件   目前图片无法传输
+ 注册功能、注销功能
+ 退出后端已有文件应清空
+ 返回前端当前路径一级目录 



返回前端一个bool值flag，表示请求是否成功；一个str值message表示错误讯息

flag为true时，message为空；flag为false时，message指出具体错误（如文件不存在，文件名重复。。。）



# API

### 注册

```python
@app.route('/signup', method = ["POST", "GET"])
def signup()
```

+ 传入参数 userName userPassword
+ post表单形式传入参数，或get传入参数
+ 返回值为一个json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复。。。）



### 登陆

```python
@app.route('/login', method = ["POST", "GET"])
def login()
```

+ 传入参数 userName userPassword
+ post表单形式传入参数，或get传入参数
+ 返回值为一个json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复。。。）
+ 成功登陆则json还会返回`path_list`，是一个字典列表，含有该用户根目录下一级文件和文件夹名字



### 注销

```python
@app.route('/logout/<username>', method = "POST")
def logout(username)
```

+ url要提供当前用户的用户名，比对成功后当前用户登出系统



### 重命名

```python
@app.route('/rename/<username>', method ="POST")
def rename(username)
```

+ url提供当前用户用户名
+ json形式传入两参数`src`、`dst`，`src`为原本路径，`dst`为更改后路径，路径从用户名一级开始（如 `xiaoming/... `）
+ 返回值为一个json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复。。。）
+ 重命名成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



### 删除

```python
@app.route('./delete/<username>', method = "POST")
def delete(username)
```

+ url提供当前用户用户名
+ json形式传入两参数`src`、`type`，`src`为原本路径，`type`有两个可选值`"folder"`和`"file"`，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值为一个json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复。。。）
+ 删除成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



### 新建文件夹

```python
@app.route('./mkdir/<username>', method = "POST")
def mkdir(username)
```

+ url提供当前用户用户名
+ json形式传入参数`src`，`src`为新文件夹的路径，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值为一个json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复。。。）
+ 新建成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



### 新建文件

```python
@app.route('./touch/<username>', method = "POST")
def touch(username):
```

+ url提供当前用户用户名
+ json形式传入参数`src`，`src`为新文件的路径，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值为一个json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复。。。）
+ 新建成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



## 上传文件

```python
@app.route('/upload/<username>', method = "POST")
def upload_file(username)
```

+ url提供当前用户用户名
+ json形式传入两参数`src`、`text`，`src`为新文件的路径，`text`为待上传内容字符串，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值为一个json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复。。。）
+ 上传成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



### 下载文件

```python
@app.route('/download/<username>', method = "GET")
def download_file(username)
```

+ url提供当前用户用户名
+ json形式传入参数`src`，`src`为新文件的路径，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值为一个json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复。。。）
+ 下载成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径；以及一个字符串`text`，是待下载的内容