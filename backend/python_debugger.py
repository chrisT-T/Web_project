
from pdb_ext import PdbExt
from flask import jsonify, request
from app import app, socketio
import threading
import sys
import os

pdb_input_client = {}
pdb_input_server = {}
pdb_output_client = {}
pdb_output_server = {}
pdb_instance = {}

@app.route('/pdb/getstack', methods=['POST'])
def getStack():
    data = request.get_json()
    token:str = data['token']
    print(pdb_instance.keys())
    if token in pdb_instance.keys():
        return jsonify(pdb_instance[token].get_current_stack())

@app.route('/pdb/getfunc', methods=['POST'])
def getFunc():
    data = request.get_json()
    token: str = data['token']
    if token in pdb_instance.keys():
        return pdb_instance[token].get_current_function()

@app.route('/pdb/runcmd', methods=['POST'])
def runcmd():
    data = request.get_json()
    token = data['token']
    cmd = data['cmd']
    if token in pdb_instance.keys():
        os.write(pdb_input_client[token], f'{cmd}\n'.encode())
        return {'runflag': True}
    else:
        return {'runflag': False}

@app.route('/pdb/curframe', methods=['POST'])
def get_current_frame():
    data = request.get_json()
    token = data['token']
    print(pdb_instance.keys())
    print(token)
    if token in pdb_instance.keys():
        instance: PdbExt = pdb_instance[token]
        res = instance.get_current_frame_data()
        return res
    else:
        return {'runflag': False}

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
def pdb_input(data):
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

    #p = multiprocessing.Process(target=run_pdb_process, args=(pdb_input_server[token], pdb_output_server[token], token, pdb_instance[token]), daemon=True)
    #p.start()
    t = threading.Thread(target=run_pdb_process, args=(pdb_input_server[token], pdb_output_server[token], token, pdb_instance[token]), daemon=True)
    t.start()
    socketio.start_background_task(target=forward_pdb_output)