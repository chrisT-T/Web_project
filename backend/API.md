# API

### 注册

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
  + 成功登陆则json还会返回`path_list`，是一个字典列表，含有该用户根目录下一级文件和文件夹名字



### 注销

```python
@app.route('/logout/<username>', method = "POST")
def logout(username)
```

+ 参数：
  + url中要提供当前用户的用户名 <username>，比对成功后当前用户退出系统
+ 返回值：
  + 没有发生错误，则返回 "succeed logout"


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
  + 重命名成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



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
  + 删除成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



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
  + 新建成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



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
  + 新建成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



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
  + 上传成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径



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
  + 下载成功则json还会返回`path_list`，是一个字典列表，含有该用户所有文件和文件夹路径；以及一个字符串`text`，是待下载的内容



### 返回一级目录

```python
@app.route('/show/<username>', method = "POST")
def show(username)
```
+ 参数：
  + url提供当前用户用户名
  + json形式传入参数`src`，`src`为目录的路径（路径非文件夹时会返回错误信息），路径从用户名一级开始（如 `xiaoming/... `）
+ 返回值
  + 格式：json，带键值对`flag`、`message`，flag为true时，message为空；flag为false时，message指出具体错误（如 文件不存在，文件名重复...）
  + 下载成功则json还会返回`filelist`，是一个字典列表，字典内含有该用户当前目录下文件和文件夹名字`name`，以及`type`指明是文件`file`还是文件夹`folder`



### 返回树形结构

```python
# 获取最外层tree数据结构
@app.route('/getTreeData/<username>', method = "GET")
def getTreeData(username)
	...
    obj = {
            'code': 0,
            'data': path_list,
            'flag': True,
            'message': None
        }
    ...
```
+ 参数：
  + url提供当前用户用户名
+ 返回值
  + 格式：json，其中`data`是字典列表，字典有键`name`：文件（夹）名字；`type`：文件（夹）类型，`isLeaf`；是否是叶子，即是否是文件；`id`：用于逐级访问；`path`：该文件（夹）的路径，从用户名一级开始



```python
# 根据id查询对应层级tree数据
@app.route('/getTreeChildData/<username>', method = "GET")
def getTreeChildData(username)
	...
    obj = {
            'code': 0,
            'data': path_list,
            'flag': True,
            'message': None
        }
    ...
```
+ 参数：
  + url提供当前用户用户名
  + get形式传入参数`id`，表示待展开的文件夹
+ 返回值
  + 格式:json，其中`data`是字典列表，字典有键`name`：文件（夹）名字；`type`：文件（夹）类型，`isLeaf`；是否是叶子，即是否是文件；`id`：用于逐级访问；`path`：该文件（夹）的路径，从用户名一级开始

