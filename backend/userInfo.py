# 管理用户账户信息
from tokenize import String
import os
import datetime
import sqlite3


# 用户名密码是否输入正确
def isCorrect(username: String, userpassword: String):
    if not os.path.exists('userInfo.db'):
        return False
    conn = sqlite3.connect('userInfo.db')
    cur = conn.cursor()
    select_cmd = f'''
        SELECT PWD FROM USERINFO WHERE NAME = '{username}' '''
    cur.execute(select_cmd)
    ls = cur.fetchall()
    conn.commit()
    conn.close()
    if ls == []:
        return False
    if userpassword == ls[0][0]:
        return True
    else:
        return False

# 该用户名是否已被注册
def isValid(username: String):
    if not os.path.exists('userInfo.db'):
        return True
    conn = sqlite3.connect('userInfo.db')
    cur = conn.cursor()
    select_cmd = f'''
        SELECT NAME FROM USERINFO'''
    cur.execute(select_cmd)
    ls = cur.fetchall()
    modify_ls = [i[0] for i in ls]
    conn.commit()
    conn.close()
    if username in modify_ls:
        return False
    else:
        return True


# 注册新用户
def createNewUser(username: String, userpassword: String):
    conn = sqlite3.connect('userInfo.db')
    cur = conn.cursor()
    try:
        create_cmd = '''
        CREATE TABLE IF NOT EXISTS USERINFO (
            NAME TEXT,
            PWD TEXT
        )'''
        cur.execute(create_cmd)
    except:
        print("Create table failed")
    insert_cmd = f'''
        INSERT INTO USERINFO (NAME, PWD) VALUES ('{username}', '{userpassword}')'''
    cur.execute(insert_cmd)
    conn.commit()
    conn.close()

# 保存项目的相关信息
def saveProject(src, language):
    username, proname = src.split('/')
    t = datetime.datetime.now()
    conn = sqlite3.connect('userInfo.db')
    cur = conn.cursor()
    try:
        create_cmd = f'''
        CREATE TABLE IF NOT EXISTS {username} (
            PRONAME TEXT,
            LANGUAGE TEXT,
            LASTUPDATE TEXT
        )'''
        cur.execute(create_cmd)
    except:
        print("Create table failed")
    insert_cmd = f'''
        INSERT INTO {username} (PRONAME, LANGUAGE, LASTUPDATE) VALUES ('{proname}', '{language}', '{t}')'''
    cur.execute(insert_cmd)
    conn.commit()
    conn.close()
    return str(t).split('.')[0]

# 删除项目信息
def deletepro(src):
    username, proname = src.split('/')
    conn = sqlite3.connect('userInfo.db')
    cur = conn.cursor()
    delete_cmd = f'''
        DELETE FROM {username} WHERE PRONAME = '{proname}' '''
    cur.execute(delete_cmd)
    conn.commit()
    conn.close()

# 更新项目名字
def renamepro(src, dst):
    username, proname = src.split('/')
    _, newname = dst.split('/')
    t = datetime.datetime.now()
    conn = sqlite3.connect('userInfo.db')
    cur = conn.cursor()
    update_cmd = f'''
        UPDATE {username} SET PRONAME = '{newname}', LASTUPDATE = '{t}' WHERE PRONAME = '{proname}' '''
    cur.execute(update_cmd)
    conn.commit()
    conn.close()

# 返回项目列表
def showpro(username):
    conn = sqlite3.connect('userInfo.db')
    cur = conn.cursor()
    select_cmd = f'''
        SELECT * FROM {username}'''
    try:
        cur.execute(select_cmd)
    except:
        return []
    ls = cur.fetchall()
    conn.commit()
    conn.close()
    print(ls)
    modify_ls = [(i[0], i[1], i[2].split('.')[0]) for i in ls]
    print(modify_ls)
    return modify_ls
