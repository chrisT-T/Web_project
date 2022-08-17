import random
import socket
import subprocess
from app import app, socketio
import socketio as sockio
from flask import request, Response, make_response
import requests
import pty
import select
import os

debugger_terminal_fd = {}

sio_clients = {}

# 以下各个函数都是在往新建的 debug server 转发
@app.route('/pdb/getstack', methods=['POST'])
def getStack():
    data = request.get_json()
    token:str = data['token']
    port:int = data['port']
    # request to debugger server
    res = requests.post(f'http://localhost:{port}/pdb/getstack', json={'token': token})
    return make_response(res.text, res.status_code)

@app.route('/pdb/getfunc', methods=['POST'])
def getFunc():
    data = request.get_json()
    token: str = data['token']
    port: int = data['port']
    res = requests.post(f'http://localhost:{port}/pdb/getfunc', json={'token': token})
    return make_response(res.text, res.status_code)

@app.route('/pdb/runcmd', methods=['POST'])
def runcmd():
    data = request.get_json()
    token = data['token']
    cmd = data['cmd']
    port = data['port']
    res = requests.post(f'http://localhost:{port}/pdb/runcmd', json={'token': token, 'cmd': cmd})
    return make_response(res.json(), res.status_code)

@app.route('/pdb/curframe', methods=['POST'])
def get_current_frame():
    data = request.get_json()
    token = data['token']
    port = data['port']
    res = requests.post(f'http://localhost:{port}/pdb/curframe', json={'token': token})
    return make_response(res.text, res.status_code)

@app.route('/pdb/repr', methods=['POST'])
def get_repr():
    data = request.get_json()
    token = data['token']
    repr = data['repr']
    port = data['port']
    res = requests.post(f'http://localhost:{port}/pdb/repr', json={'token': token, 'repr': repr})
    return make_response(res.text, res.status_code)

# 将一份代码进入 debug 模式，代码的输入输出会进入 debug terminal
@app.route('/pdb/debug', methods=['POST'])
def start_debug():
    data = request.get_json()
    token = data['token']
    path = data['filepath']
    port = data['port']
    res = requests.post(f'http://localhost:{port}/pdb/debug', json={'token': token, 'filepath': path})
    return make_response(res.text, res.status_code)

@app.route('/pdb/clearBreakPoint', methods=['POST'])
def clearBreakPoint():
    data = request.get_json()
    token = data['token']
    port = data['port']
    res = requests.post(f'http://localhost:{port}/pdb/clearBreakPoint', json={'token': token})
    return make_response(res.text, res.status_code)

@socketio.on('connect_to_debug_server', namespace='/debugger')
def connect_to_debugger_server(port):
    create_socketio_client_to_debug_server(port)

@socketio.on('disconnect_from_debug_server', namespace='/debugger')
def disconnect_from_debugger_server(port):
    if port in sio_clients:
        sio_clients[port].disconnect()
        del sio_clients[port]

@socketio.on('connect', namespace='/debugger')
def connect():
    pass

@socketio.on('disconnect', namespace='/debugger')
def connect():
    pass

# 轮询，将 debugger terminal 的输出发送给 client
def forward_debugger_term():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        for key in debugger_terminal_fd.keys():
            timeout_sec = 0
            (data_ready, _, _) = select.select([debugger_terminal_fd[key]], [], [], timeout_sec)
            if data_ready:
                output = os.read(debugger_terminal_fd[key], max_read_bytes).decode()
                socketio.emit("debugger_term_output", {"output": output, 'token': key}, namespace="/pdb", to=key)

# 创建一个 socketio client，转发给 app 上的 socketio
async def create_socketio_client_to_debug_server(port: int):
    print('create_socketio_client_to_debug_server!!!')
    new_client = sockio.AsyncClient()
    sio_clients[port] = new_client
    await new_client.connect(f'http://localhost:{port}', namespaces=['/pdb'])
    # socketio.emit("pdb_terminated", { 'token': key }, namespace="/pdb")
    def terminated_handler(token):
        socketio.emit("pdb_terminated", { "token": token, "port": port }, namespace="/debugger")
    new_client.on('pdb_terminated', terminated_handler)
    # socketio.emit("pdb_output", {"consoleOutput": output, 'token': token}, namespace="/pdb", to=token)
    def output_handler(consoleOutput, token):
        socketio.emit("pdb_output", {"consoleOutput": consoleOutput, 'token': token}, namespace="/debugger", to=token)
    new_client.on('pdb_output', output_handler)
    # socketio.emit("pdb_quit", {'token': token, 'flag': flag }, namespace="/pdb", to=token)
    def quit_handler(token, flag):
        socketio.emit("pdb_quit", {"token": token, "flag": flag}, namespace="/debugger", to=token)
    new_client.on('pdb_quit', quit_handler)

# debugger terminal 的文字输入                
@socketio.on('debugger_term_input', namespace='/pdb')
def pdb_terminal_input(data):
    token = request.sid
    print(token, debugger_terminal_fd.keys())
    if token in debugger_terminal_fd.keys():
        os.write(debugger_terminal_fd[token], data['input'].encode())



# 当有新的 session id 的时候，新建一个 Flask + Pdb 的进程，同时在子线程中新建一个 bash
@socketio.on("connect", namespace='/pdb')
def debugger_connect():
    token = request.sid
    if token in debugger_terminal_fd.keys():
        return
    
    (child_pid, fd) = pty.fork()

    if child_pid == 0:
        # child process
        subprocess.run('bash')
    else:
        # parent process
        debugger_terminal_fd[token] = fd
        socketio.start_background_task(target=forward_debugger_term)
        print('create new debug server')
        port = random.randint(10000, 30000)
        while is_port_in_use(port):
            port = random.randint(10000, 30000)
        print(f'port is {port}')
        os.write(fd, 'export FLASK_APP=debugger_server\n'.encode())
        os.write(fd, f'flask run -p {port}\n'.encode())
        socketio.emit('debugger_port_allocated', {"port": port, 'token': token}, namespace='/pdb', to=token)

@socketio.on('disconnect', namespace='/pdb')
def debugger_disconnect():
    debugger_terminal_fd.pop(request.sid)
    if request.sid in sio_clients:
        sio_clients[request.sid].disconnect()
        del sio_clients[request.sid]


def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0