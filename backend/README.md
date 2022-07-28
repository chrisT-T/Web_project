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