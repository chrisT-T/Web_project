import argparse
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_cors import CORS
import pty
import os
import subprocess
import select
import termios
import struct
import fcntl
import shlex
import logging
import sys

app = Flask(__name__, template_folder='.')
CORS(app, resources=r'/*')
app.config["fd"] = None
app.config["child_pid"] = None

# cmd for win
app.config['cmd'] = 'bash'

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    if app.config['fd']:
        os.write(app.config['fd'], data['input'].encode())

def forward_pty_output():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        if app.config["fd"]:
            timeout_sec = 0
            (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
            if data_ready:
                output = os.read(app.config["fd"], max_read_bytes).decode()
                socketio.emit("pty-output", {"output": output}, namespace="/pty")

@app.route('/run', methods=['POST'])
def run():
    data = request.get_json()
    os.write(app.config['fd'], 'python3 test.py\n'.encode())

@socketio.on("connect", namespace='/pty')
def connect() :
    print('new client')
    if app.config['child_pid']:
        return
    (child_pid, fd) = pty.fork()

    if child_pid == 0:
        subprocess.run(app.config['cmd'])
    else:
        app.config['fd'] = fd
        app.config['child_pid'] = child_pid
        socketio.start_background_task(target=forward_pty_output)
        

if __name__ == "__main__":
    socketio.run(app, port=5000, host='127.0.0.1')