## Debugger API

**执行 PDB 命令**

```py
@app.route('/pdb/runcmd', methods=['POST'])
def runcmd():
```

参数:

```json
{ 
  token: string, 
  cmd: string 
}
```

返回值:
```json
{
  runflag: bool
}
```
表示命令是否被执行，注意不需要输入换行符。

**获取当前 PDB 的信息**
```py
@app.route('/pdb/curframe', methods=['POST'])
def get_current_frame():
```

参数:

```json
{ 
  token: string, 
}
```

返回值：

```json
{
    'dirname': string,
    'filename': string,
    'file_listing': string,
    'current_line': int,
    'breakpoints': [int],
    'globals': string,
    'locals': string
}
```

**获取调用栈信息**

```py
@app.route('/pdb/getstack', methods=['POST'])
def getStack():
```

参数：
```json
{
    token: string
}
```

返回值: List of string

**获取当前函数名称**

```py
@app.route('/pdb/getfunc', methods=['POST'])
def getFunc():
```

参数：
```json
{
    token: string
}
```

返回值: List of string

**开始调试**

```py
@app.route('/pdb/debug', methods=['POST'])
def start_debug():
```

参数：
```json
{
    token: string,
    filepath: string
}
```

**调试结束**

```py
socketio.emit("pdb_quit", {'token': token}, namespace="/pdb")
```