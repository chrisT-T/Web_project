from app import app, socketio
from flask import request
import os
import subprocess
import pty

@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    token = request.sid
    if app.config['fd'][token]:
        os.write(app.config['fd'][token], data['input'].encode())

def forward_pty_output(token: str):
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        for token in app.config['fd'].keys():
            if app.config["fd"][token]:
                output = os.read(app.config["fd"][token], max_read_bytes).decode()
                socketio.emit("pty-output", {"output": output, 'token': token}, namespace="/pty", to=token)

@socketio.on('disconnect', namespace='/pty')
def disconnect() :
    token = request.sid
    app.config['fd'].pop(token)
    app.config['child_pid'].pop(token)
    print(token, 'terminal disconnected')

@socketio.on("connect", namespace='/pty')
def connect() :
    token = request.sid
    
    if token in app.config['child_pid'].keys():
        return

    (child_pid, fd) = pty.fork()

    if child_pid == 0:
        subprocess.run(app.config['cmd'])
    else:
        app.config['fd'][token] = fd
        app.config['child_pid'][token] = child_pid
        socketio.start_background_task(target=forward_pty_output, token=token)
