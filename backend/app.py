from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

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