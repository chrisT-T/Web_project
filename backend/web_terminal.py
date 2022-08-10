from app import app, socketio
from flask import request
import os
import select
import subprocess
import pty

@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    if app.config['fd'][data['token']]:
        os.write(app.config['fd'][data['token']], data['input'].encode())

def forward_pty_output():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        for key in app.config['fd'].keys():
            if app.config["fd"][key]:
                timeout_sec = 0
                (data_ready, _, _) = select.select([app.config["fd"][key]], [], [], timeout_sec)
                if data_ready:
                    output = os.read(app.config["fd"][key], max_read_bytes).decode()
                    socketio.emit("pty-output", {"output": output, 'token': key}, namespace="/pty")

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    os.write(app.config['fd'][data.get('token')], f"python3 { data.get('path') } \n".encode())

@app.route('/runpdb', methods=['POST'])
def runpdb():
    data = request.get_json()
    os.write(app.config['fd'][data.get('token')], f"python3 -m pdb { data.get('path') } \n".encode())

@socketio.on("connect", namespace='/pty')
def connect(data) :
    print('new client', data['token'])

    token = data['token']

    if token in app.config['child_pid'].keys():
        return

    (child_pid, fd) = pty.fork()

    if child_pid == 0:
        subprocess.run(app.config['cmd'])
    else:
        app.config['fd'][token] = fd
        app.config['child_pid'][token] = child_pid
        socketio.start_background_task(target=forward_pty_output)
