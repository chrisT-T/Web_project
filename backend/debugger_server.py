from crypt import methods
from curses import tparm
import random
from pdb_ext import PdbExt
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
import threading
import sys
import os
import argparse
import time
import atexit

app = Flask(__name__, template_folder='.')
CORS(app, resources=r'/*')
socketio = SocketIO(app, cors_allowed_origins="*")

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.FATAL)

pdb_input_client = {}
pdb_input_server = {}
pdb_output_client = {}
pdb_output_server = {}

pdb_instance = {}
pdb_instance_lock = threading.Lock()

@app.route('/pdb/getstack', methods=['POST'])
def getStack():
    data = request.get_json()
    token:str = data['token']
    pdb_instance_lock.acquire()
    if token in pdb_instance.keys():
        res = jsonify(pdb_instance[token].get_current_stack())
        pdb_instance_lock.release()
        return res
    else:
        return {'runFlag': 'Token doesnot exist'}

@app.route('/pdb/getfunc', methods=['POST'])
def getFunc():
    data = request.get_json()
    token: str = data['token']
    pdb_instance_lock.acquire()
    if token in pdb_instance.keys():
        res = pdb_instance[token].get_current_function()
        pdb_instance_lock.release()
        return res

@app.route('/pdb/runcmd', methods=['POST'])
def runcmd():
    data = request.get_json()
    token = data['token']
    cmd = data['cmd']
    pdb_instance_lock.acquire()
    if token in pdb_instance.keys():
        os.write(pdb_input_client[token], f'{cmd}\n'.encode())
        pdb_instance_lock.release()
        return {'runflag': True}
    else:
        pdb_instance_lock.release()
        return {'runflag': False}

@app.route('/pdb/curframe', methods=['POST'])
def get_current_frame():
    data = request.get_json()
    token = data['token']
    pdb_instance_lock.acquire()
    if token in pdb_instance.keys():
        instance: PdbExt = pdb_instance[token]
        res = instance.get_current_frame_data()
        pdb_instance_lock.release()
        return res
    else:
        return {'runflag': False}

@app.route('/pdb/repr', methods=['POST'])
def get_repr():
    data = request.get_json()
    token = data['token']
    repr = data['repr']
    pdb_instance_lock.acquire()
    if token in pdb_instance.keys():
        instance: PdbExt = pdb_instance[token]
        res = instance.get_repr_value(repr)
        pdb_instance_lock.release()
        return res
    else:
        return {'runflag': False}

def forward_pdb_output(token: str):
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        pdb_instance_lock.acquire()
        flag: bool = token in pdb_instance.keys()
        pdb_instance_lock.release()
        try:
            if flag:
                output = os.read(pdb_output_client[token], max_read_bytes).decode()
                socketio.emit("pdb_output", {"consoleOutput": output, 'token': token}, namespace="/pdb")
        finally:
            pass

# 将一份代码进入 debug 模式，代码的输入输出会进入 debug terminal
@app.route('/pdb/debug', methods=['POST'])
def start_debug():
    data = request.get_json()
    token = data['token']
    path = data['filepath']
    def run_pdb_process(token, instance:PdbExt):
        flag: str  = 'success'
        try:
            PdbExt._runscript(instance, os.path.realpath(path))
        except FileNotFoundError:
            flag = 'FileNotFoundError'

        time.sleep(0.2)
        pdb_instance_lock.acquire()
        pdb_input_client.pop(token)
        pdb_input_server.pop(token)
        pdb_output_client.pop(token)
        pdb_output_server.pop(token)
        pdb_instance.pop(token)
        pdb_instance_lock.release()
        
        socketio.emit("pdb_quit", {'token': token, 'flag': flag }, namespace="/pdb")
        
    t = threading.Thread(target=run_pdb_process, args=(token, pdb_instance[token]), daemon=True)
    t.start()
    return f'{token} debugging {path}'

@app.route('/pdb/clearBreakPoint', methods=['POST'])
def clearBreakPoint():
    data = request.get_json()
    token = data['token']
    pdb_instance_lock.acquire()
    if token in pdb_instance.keys():
        instance: PdbExt = pdb_instance[token]
        instance.clear_all_breaks()
        pdb_instance_lock.release()
        return {'runflag': True}
    else:
        pdb_instance_lock.release()
        return {'runflag': False }

# 连接：新建一个 Pdb 实例，并将其（Pdb）输入输出用管道导出
@socketio.on("connect_to_pdb", namespace='/pdb')
def pdb_connect(data):
    token = data['token']
    socketio.emit('clear_screen', { 'token': token }, namespace="/pdb", to=request.sid)
    if token in pdb_input_server.keys():
        return

    pdb_input_server[token], pdb_input_client[token] = os.pipe()
    pdb_output_client[token], pdb_output_server[token] = os.pipe()
    pdb_instance[token] = PdbExt(stdin=os.fdopen(pdb_input_server[token], 'r'), stdout=os.fdopen(pdb_output_server[token], 'w'))
    socketio.start_background_task(target=forward_pdb_output, token=token)

@socketio.on("connect", namespace='/pdb')
def connect():
    pass

@app.route('/pdb/backdoor')
def debug_backdoor() :
    socketio.stop()

@socketio.on("disconnect_from_pdb", namespace='/pdb')
def pdb_disconnect():
    token = request.sid
    pdb_instance_lock.acquire()
    if token in pdb_instance.keys():
        pdb_input_client.pop(token)
        pdb_input_server.pop(token)
        pdb_output_client.pop(token)
        pdb_output_server.pop(token)
        pdb_instance.pop(token)
    pdb_instance_lock.release()

@socketio.on("disconnect", namespace='/pdb')
def disconnect():
    pass

@atexit.register
def atexit_function() :
    for key in pdb_instance.keys():
        socketio.emit("pdb_terminated", { 'token': key }, namespace="/pdb")
    time.sleep(0.2)
