import argparse
from matplotlib import mlab
from pdb_ext import PdbExt
import multiprocessing
from multiprocessing.managers import BaseManager
from flask import Flask, render_template, request
from flask_socketio import SocketIO, disconnect
from flask_cors import CORS
import pty
import os
import subprocess
import select
import sys
import threading

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

pdb_input_client = {}
pdb_input_server = {}
pdb_output_client = {}
pdb_output_server = {}
pdb_instance = {}

@app.route('/cmd', methods=['POST'])
def runcmd():
    data = request.get_json()
    token = data['token']
    cmd = data['cmd']
    if token in pdb_instance.keys():
        os.write(pdb_input_client[token], f'{cmd}\n'.encode())
    print(cmd)
    return 'cmd send succedd'

@app.route('/setbreak', methods=['POST'])
def setBreak():
    data = request.get_json()
    token = data['token']
    line = data['breakpoint']
    if token in pdb_instance.keys():
        os.write(pdb_input_client[token], f'b {line}\n'.encode())
    return 'true'

@app.route('/pdbN', methods=['POST'])
def pdbN():
    data = request.get_json()
    token = data['token']
    print(pdb_instance.keys())
    print(token)
    if token in pdb_instance.keys():
        instance: PdbExt = pdb_instance[token]
        res = instance.my_get_curframe_locals()
        print(res)
    return "test"

def forward_pdb_output():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        for key in pdb_output_client.keys():
            if key not in pdb_instance.keys():
                print(pdb_instance.keys(), pdb_output_client.keys())
                continue
            output = os.read(pdb_output_client[key], max_read_bytes).decode()
            socketio.emit("pdb-output", {"consoleOutput": output, 'token': key}, namespace="/pdb")

@socketio.on("pdb-input", namespace="/pdb")
def pty_input(data):
    token = data['token']
    if token in pdb_input_client.keys():
        print(data['input'])
        os.write(pdb_input_client[token], data['input'].encode())

@socketio.on("connect", namespace='/pdb')
def pdb_connect(data):
    token = data['token']
    print(token)
    if token in pdb_input_server.keys():
        return

    pdb_input_server[token], pdb_input_client[token] = os.pipe()
    pdb_output_client[token], pdb_output_server[token] = os.pipe()
    stdout_tmp = sys.stdout
    sys.stdout = stdout_tmp
    pdb_instance[token] = PdbExt(stdin=os.fdopen(pdb_input_server[token], 'r'), stdout=os.fdopen(pdb_output_server[token], 'w'))
    def run_pdb_process(input_fd, output_fd, token, instance:PdbExt):
        
        PdbExt._runscript(instance, os.path.realpath('./test.py'))
        #instance.set_trace()
        sys.stdout.flush()
        os.close(input_fd)
        os.close(output_fd)
        pdb_input_client.pop(token)
        pdb_input_server.pop(token)
        pdb_output_client.pop(token)
        pdb_output_server.pop(token)
        pdb_instance.pop(token)
        print('pdb finish')
        disconnect(namespace='/pdb')

    #p = multiprocessing.Process(target=run_pdb_process, args=(pdb_input_server[token], pdb_output_server[token], token, pdb_instance[token]), daemon=True)
    #p.start()
    t = threading.Thread(target=run_pdb_process, args=(pdb_input_server[token], pdb_output_server[token], token, pdb_instance[token]), daemon=True)
    t.start()
    socketio.start_background_task(target=forward_pdb_output)

if __name__ == "__main__":
    socketio.run(app, port=5000, host='127.0.0.1')