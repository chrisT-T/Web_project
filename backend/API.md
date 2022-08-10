# API

### 注册并登录

```python
@app.route('/signup', method = ["POST", "GET"])
def signup()
```

+ 参数： `userName` `userPassword`
  + post表单形式传入参数，或get传入参数
+ 返回值：
  + 格式json，有`flag`、`message`两个属性，`flag`为true时，代表`message`为空；`flag`为false时，`message`中含有具体错误类型（如 文件不存在，文件名重复...）


### 登陆

```python
@app.route('/login', method = ["POST", "GET"])
def login()
```

+ 参数： `userName` `userPassword`
  + post表单形式传入参数，或get传入参数
+ 返回值：
  + 格式：json，带键值对`flag`、`message`，`flag`为true时，代表`message`为空；`flag`为false时，`message`中含有具体错误类型（如 文件不存在，文件名重复...）



### 注销

```python
@app.route('/logout/<username>', method = "POST")
def logout(username)
```

+ 参数：
  + url中要提供当前用户的用户名 <username>，比对成功后当前用户退出系统
+ 返回值：
  + 没有发生错误，则返回 "succeed logout"

### 项目重命名
```python
@app.route('/renamepro/<username>', methods =["POST"])
def renamepro(username):
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入两参数`src`、`dst`，`src`为原本项目路径，`dst`为更改后项目路径，路径从用户名一级开始（如 `xiaoming/... `）
+ 返回值：
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）

### 重命名

```python
@app.route('/rename/<username>', method ="POST")
def rename(username)
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入两参数`src`、`dst`，`src`为原本路径，`dst`为更改后路径，路径从用户名一级开始（如 `xiaoming/... `）
+ 返回值
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）

### 删除项目
```python
@app.route('/deletepro/<username>', methods = ["POST"])
def deletepro(username):
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入参数`src`，`src`为项目路径，路径从用户名一级开始（如 `xiaoming/... `）
+ 返回值
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）
### 删除

```python
@app.route('./delete/<username>', method = "POST")
def delete(username)
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入两参数`src`、`type`，`src`为原本路径，`type`有两个可选值`"folder"`和`"file"`，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）

### 新建项目
```python
@app.route('/mkpro/<username>', methods = ["POST"])
def mkpro(username):
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入参数`src`，`src`为新文件夹的路径，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值：
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）

### 新建文件夹

```python
@app.route('./mkdir/<username>', method = "POST")
def mkdir(username)
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入参数`src`，`src`为新文件夹的路径，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值：
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）



### 新建文件

```python
@app.route('./touch/<username>', method = "POST")
def touch(username):
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入参数`src`，`src`为新文件的路径，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）


## 上传文件

```python
@app.route('/upload/<username>', method = "POST")
def upload_file(username)
```

+ 参数：
  + url提供当前用户用户名
  + json形式传入两参数`src`、`text`，`src`为文件的路径，`text`为待上传内容字符串，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）



### 下载文件

```python
@app.route('/download/<username>', method = "GET")
def download_file(username)
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入参数`src`，`src`为文件的路径，路径从用户名一级开始（如 `xiaoming/... `）

+ 返回值
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）

### 获取项目列表
```python
@app.route('/getPro/<username>', methods = ["GET"])
def getPro(username):
```
+ 参数：
  + url提供当前用户用户名
+ 返回值
  + 格式：json，带键值对`flag`、`message`、`data`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）,`data` 中为项目列表

### 获取项目文件树
```python
@app.route('/getFileTree/<username>/<projectname>', methods = ["GET"])
def getFileTree(username, projectname):
```
+ 参数：
  + url提供当前用户用户名和项目名
+ 返回值
  + 格式：json，带键值对`flag`、`message`、`fileTree`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）,`fileTree` 中为项目文件树