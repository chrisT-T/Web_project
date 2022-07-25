# 管理用户账户信息
from tokenize import String

user_list = []

def isValid(username: String, userpassword: String):
    for user in user_list:
        if user['name'] == username: 
            if user['password'] == userpassword:
                return True
            else:
                return False
    # 该用户为新用户
    new_user = {}
    new_user['name'] = username
    new_user['password'] = userpassword
    user_list.append(new_user)
    return True