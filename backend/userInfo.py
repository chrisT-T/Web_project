# 管理用户账户信息
from tokenize import String

user_list = []
cur_user = ''

# 用户名密码是否输入正确
def isCorrect(username: String, userpassword: String):
    for user in user_list:
        if user['name'] == username: 
            if user['password'] == userpassword:
                return True
            else:
                return False
    return False

# 该用户名是否已被注册
def isValid(username: String):
    for user in user_list:
        if user['name'] == username: 
            return False
    return True

# 注册新用户
def createNewUser(username: String, userpassword: String):
    new_user = {}
    new_user['name'] = username
    new_user['password'] = userpassword
    user_list.append(new_user)


def setCurUser(username: String):
    global cur_user
    cur_user = username

def currentUser():
    return cur_user

# setCurUser("xiaohong")
# print (currentUser())