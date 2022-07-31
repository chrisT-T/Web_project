# 管理用户账户信息
from tokenize import String, group
import pandas as pd
from openpyxl import load_workbook
import os

cur_user = ''

# 用户名密码是否输入正确
def isCorrect(username: String, userpassword: String):
    if not os.path.exists("./userInfo.xlsx"):
        return False
    else:
        df = pd.DataFrame(pd.read_excel('./userInfo.xlsx', sheet_name="userInfo"))
        result = df[(df.username==username) & (df.password==userpassword)]
        return not result.empty

# 该用户名是否已被注册
def isValid(username: String):
    if not os.path.exists("./userInfo.xlsx"):
        return True
    else:
        df = pd.DataFrame(pd.read_excel('./userInfo.xlsx', sheet_name="userInfo"))
        userList = df['username']
        if username not in userList.values:
            return True
    return False


# 注册新用户
def createNewUser(username: String, userpassword: String):
    if not os.path.exists("./userInfo.xlsx"):
        df = pd.DataFrame([{'username' : username, 'password' : userpassword}])
        df.to_excel("./userInfo.xlsx", sheet_name="userInfo", index=False)
        return
    else:
        df_old = pd.DataFrame(pd.read_excel('./userInfo.xlsx', sheet_name="userInfo"))
        n = len(df_old.index)
        df = pd.DataFrame([{'username' : username, 'password' : userpassword}])
        book = load_workbook('./userInfo.xlsx')
        group_writer = pd.ExcelWriter('./userInfo.xlsx', engine='openpyxl')
        group_writer.book = book
        group_writer.sheets = dict((ws.title, ws) for ws in book.worksheets)
        df_rows = df_old.shape[0]
        df.to_excel(group_writer, sheet_name='userInfo', startrow=df_rows+1,header=False, index=False)
        group_writer.save()
        return


def setCurUser(username: String):
    global cur_user
    cur_user = username

def currentUser():
    return cur_user
