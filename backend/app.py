from pdb_ext import PdbExt
from flask import Flask, jsonify, render_template, request
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

import python_debugger
import web_terminal

if __name__ == "__main__":
    socketio.run(app, port=5000, host='127.0.0.1')