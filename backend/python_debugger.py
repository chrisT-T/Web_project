from argparse import Namespace
import subprocess
from socket import SocketIO
from app import app, socketio
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
                socketio.emit("debugger_term_output", {"output": output, 'token': key}, namespace="/pdb")

@socketio.on('debugger_term_input', namespace='/pdb')
def pdb_terminal_input(data):
    if data['token'] in debugger_terminal_fd.keys():
        os.write(debugger_terminal_fd[data['token']], data['input'].encode())

@socketio.on("connect", namespace='/pdb')
def debugger_connect(data):
    token = data['token']
    if token in debugger_terminal_fd.keys():
        return
    
    (child_pid, fd) = pty.fork()

    if child_pid == 0:
        subprocess.run('bash')
    else:
        debugger_terminal_fd[token] = fd
        socketio.start_background_task(target=forward_debugger_term)
        os.write(fd, 'export FLASK_APP=debugger_server\n'.encode())
        os.write(fd, 'flask run -p 2333\n'.encode())
        socketio.emit('debugger_port', {"port": 2333, 'token': token}, namespace='/pdb')