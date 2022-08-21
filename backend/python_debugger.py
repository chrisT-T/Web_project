from argparse import Namespace
import random
import socket
import subprocess
from time import sleep
from traceback import print_tb
from xmlrpc.client import boolean
from app import app, socketio
import socketio as sockio
from flask import request, Response, make_response
import requests
import pty
import select
import os

debugger_terminal_fd = {}

'''
    get the terminal token by port
'''
debugger_terminal_token = {}

sio_clients = {}

@app.route('/pdb/backdoor')
def debug_backdoor() :
    return str(sio_clients.keys())

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
def connect_to_debugger_server(data):
    token = request.sid
    port = data['port']
    if create_socketio_client_to_debug_server(port, token):
        socketio.emit('connect_to_debug_server_success', {'port': port }, namespace='/debugger', to=request.sid)
        print('connect to new debug server on port' + str(port))

@socketio.on('disconnect_from_debug_server', namespace='/debugger')
def disconnect_from_debugger_server(data):
    port = data['port']
    if port in sio_clients:
        sio_clients[port].emit('disconnect_from_pdb', namespace='/pdb')
        del sio_clients[port]

@socketio.on('connect', namespace='/debugger')
def connect():
    print('connect debugger')

@socketio.on('disconnect', namespace='/debugger')
def connect():
    print('disconnect debugger')

# 轮询，将 debugger terminal 的输出发送给 client
def forward_debugger_term(key: str):
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        try:
            if key in debugger_terminal_fd.keys():
                timeout_sec = 0
                (data_ready, _, _) = select.select([debugger_terminal_fd[key]], [], [], timeout_sec)
                if data_ready:
                    output = os.read(debugger_terminal_fd[key], max_read_bytes).decode()
                    socketio.emit("debugger_term_output", {"output": output, 'token': key}, namespace="/pdb", to=key)
        except:
            pass

# 创建一个 socketio client，转发给 app 上的 socketio
def create_socketio_client_to_debug_server(port: int, token: str) -> boolean:
    print('create_socketio_client_to_debug_server!!!')
    tmp = 0
    while (not is_port_in_use(port)):
        sleep(0.1)
        tmp += 0.1
        if tmp > 8:
            print(f'{port}: {token} connect forward exit')
            return False
        pass
    new_client = sockio.Client()
    sio_clients[port] = new_client
    new_client.connect('http://localhost:' + str(port), namespaces=['/pdb'])
    new_client.emit('connect_to_pdb', {'token': token}, namespace='/pdb')
    # socketio.emit("pdb_terminated", { 'token': key }, namespace="/pdb")
    def terminated_handler(data):
        print("terminated_handler")
        socketio.emit("pdb_terminated", data, namespace="/debugger", to=token)
    new_client.on('pdb_terminated', terminated_handler, namespace='/pdb')
    # socketio.emit("pdb_output", {"consoleOutput": output, 'token': token}, namespace="/pdb", to=token)
    def output_handler(data):
        print("output_handler")
        socketio.emit("pdb_output", data, namespace="/debugger", to=token)
    new_client.on('pdb_output', output_handler, namespace='/pdb')
    # socketio.emit("pdb_quit", {'token': token, 'flag': flag }, namespace="/pdb", to=token)
    def quit_handler(data):
        print("quit_handler")
        socketio.emit("pdb_quit", data, namespace="/debugger", to=token)
    new_client.on('pdb_quit', quit_handler, namespace='/pdb')

    def clear_screen_handler(data):
        socketio.emit('clear_screen', namespace="/pdb", to=debugger_terminal_token[port])
    new_client.on('clear_screen', clear_screen_handler, namespace='/pdb')

    print('create_socketio_client_to_debug_server success')
    return True

# debugger terminal 的文字输入                
@socketio.on('debugger_term_input', namespace='/pdb')
def pdb_terminal_input(data):
    token = request.sid
    print(token, debugger_terminal_fd.keys())
    if token in debugger_terminal_fd.keys():
        os.write(debugger_terminal_fd[token], data['input'].encode())

@app.route('/pdb/inputbyport', methods=['POST'])
def debugger_term_input_by_port():
    data = request.get_json()
    port = data['port']
    cmd = data['cmd']
    token = debugger_terminal_token[port]
    if token in debugger_terminal_fd.keys():
        os.write(debugger_terminal_fd[token], cmd.encode())
        return make_response('success', 200)
    else:
        return make_response('no terminal cooresponds to the port', 500)


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
        socketio.start_background_task(target=forward_debugger_term, key=token)
        print('create new debug server')
        port = random.randint(10000, 30000)
        while is_port_in_use(port):
            port = random.randint(10000, 30000)
        print(f'port is {port}')

        debugger_terminal_token[port] = token
        
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