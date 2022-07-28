import argparse
import pdb
import multiprocessing
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_cors import CORS
import pty
import os
import subprocess
import select


app = Flask(__name__, template_folder='.')
CORS(app, resources=r'/*')
app.config["fd"] = {}
app.config["child_pid"] = {}

# cmd for win
app.config['cmd'] = 'bash'

socketio = SocketIO(app, cors_allowed_origins="*")

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

@app.route('/pdbN', methods=['POST'])
def pdbN():
    data = request.get_json()
    os.write(app.config['fd'][data.get('token')], f"n \n".encode())

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

input_server = input_client = output_client = output_server = None
pdbtoken = None

def forward_pdb_output():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        if output_client != None:
            print(output_client)
            output = os.read(output_client, max_read_bytes).decode()
            print(output)
            socketio.emit("pdb-output", {"consoleOutput": output, 'token': pdbtoken}, namespace="/pdb")

@socketio.on("pdb-input", namespace="/pdb")
def pty_input(data):
    if input_client != None:
        print(data['input'])
        os.write(input_client, data['input'].encode())

@socketio.on("connect", namespace='/pdb')
def pdb_connect(data):
    token = data['token']
    
    global input_server, output_server, output_client, input_client, pdbtoken
    pdbtoken = token

    if input_server != None:
        return

    input_server, input_client = os.pipe()
    output_client, output_server = os.pipe()

    def run_pdb_process(input_fd, output_fd):
        pdb_instance = pdb.Pdb(stdin=os.fdopen(input_fd, 'r'), stdout=os.fdopen(output_fd, 'w'))
        pdb.Pdb._runscript(pdb_instance, './test.py')
        print('pdb finish')
    p = multiprocessing.Process(target=run_pdb_process, args=(input_server, output_server), daemon=True)
    p.start()
    socketio.start_background_task(target=forward_pdb_output)




if __name__ == "__main__":
    socketio.run(app, port=5000, host='127.0.0.1')