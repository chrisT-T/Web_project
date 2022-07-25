## 后端接口

+ 登陆
  + 接收前端的用户名和密码，将该用户的文件目录返还
  + 需要注册页面和对应接口，同时登陆时判断用户名密码是否正确，暂时可在首次登陆时创建账户
+ 注销
+ 文件传输
  + 新建文件/项目
  + 保存文件/项目
  + 打开文件/项目
  + 文件树保存形式：文件？   `backend/secure`



> 文件上传以表单形式  必须要设置好请求头
>
> ```html
> <form action="http://localhost:7787/files" enctype="multipart/form-data" method="POST">
>   <input name="file" type="file" id="file">
>   <input type="submit" value="提交">
> </form>
> ```