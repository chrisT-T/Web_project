import random
import socket
import subprocess
from app import app, socketio
from flask import request
import pty
import select
import os

debugger_terminal_fd = {}

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
                
@socketio.on('debugger_term_input', namespace='/pdb')
def pdb_terminal_input(data):
    token = request.sid
    print(token, debugger_terminal_fd.keys())
    if token in debugger_terminal_fd.keys():
        os.write(debugger_terminal_fd[token], data['input'].encode())

@socketio.on("connect", namespace='/pdb')
def debugger_connect():
    token = request.sid
    if token in debugger_terminal_fd.keys():
        return
    
    (child_pid, fd) = pty.fork()

    if child_pid == 0:
        subprocess.run('bash')
    else:
        debugger_terminal_fd[token] = fd
        socketio.start_background_task(target=forward_debugger_term)
        print('testawets')
        port = random.randint(10000, 30000)
        while is_port_in_use(port):
            port = random.randint(10000, 30000)
        print(f'port is {port}')
        os.write(fd, 'export FLASK_APP=debugger_server\n'.encode())
        os.write(fd, f'flask run -p {port}\n'.encode())
        socketio.emit('debugger_port', {"port": port, 'token': token}, namespace='/pdb', to=token)

@socketio.on('disconnect', namespace='/pdb')
def debugger_disconnect():
    debugger_terminal_fd.pop(request.sid)

def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0