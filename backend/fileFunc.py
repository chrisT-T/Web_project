import os
from tokenize import String

# 文件根目录
FILE_PATH = "./userfile/"

# 新建文件夹
def mkdir(path: String):
    path = FILE_PATH + path
    folder = os.path.exists(path)
    # 文件夹不存在 新建
    if not folder:
        os.makedirs(path)
        print ("create new folder: "+path)
        print ("----------------------")
    else:
        print (path + " the folder has existed")
        print ("----------------------")
    
# mkdir("xiaoming")