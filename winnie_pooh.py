import threading
from flask import Flask, request
from pymongo import MongoClient
from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
import logging
import socket
import datetime

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

app = Flask(__name__)

client = MongoClient('mongodb://localhost:27069/')
db = client.honeypot_logs

# MongoDB (logging)
def log_to_mongodb(service, client_ip, data):
    try:
        log_entry = {
            'service': service,
            'timestamp': datetime.datetime.now(),
            'client_ip': client_ip,
            'data': data
        }
        db.logs.insert_one(log_entry)
        log.info(f'Logged to MongoDB: {log_entry}')
    except Exception as e:
        log.error(f'Error logging to MongoDB: {e}')

# SSH
def start_ssh_server():
    host = '0.0.0.0'
    port = 2222
    log.info(f'Starting SSH server')

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ssh_socket:
            ssh_socket.bind((host, port))
            ssh_socket.listen(5)
            log.info(f'SSH server is running on {host}:{port}')

            while True:
                client_socket, client_address = ssh_socket.accept()
                client_ip = client_address[0]
                client_socket.sendall(b'SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n')
                data = client_socket.recv(1024).decode('utf-8', errors='ignore')
                log.info(f'Client {client_ip} sent: {data}')
                log_to_mongodb('ssh', client_ip, data)
                client_socket.close()
    except Exception as e:
        log.error(f'SSH server error: {e}')

# HTTP  
@app.route('/')
def http_pot():
    client_ip = request.remote_addr
    log.info(f'Client {client_ip} connected to HTTP pot')
    log_to_mongodb('http', client_ip, {"path": request.path, "headers": dict(request.headers), "args": dict(request.args)})
    return 'Under construction!', 200

def start_http_server():
    host = '0.0.0.0'
    port = 8080
    log.info(f'Starting HTTP server')
    try:
        app.run(host=host, port=port)
        log.info(f'HTTP server is running on {host}:{port}')
    except Exception as e:
        log.error(f'HTTP server error: {e}')

# FTP
def start_ftp_server():
    authorizer = DummyAuthorizer()
    log.info(f'Starting FTP server')
    
    authorizer.add_user("user", "password", "/tmp", perm="elradfmw")
    authorizer.add_anonymous("/tmp", perm="elradfmw")
    
    handler = FTPHandler
    handler.authorizer = authorizer
    
    def log_ftp_activity(event_handler):
        client_ip = event_handler.remote_ip
        data = {
            'command': event_handler.command,
            'argument': event_handler.command_arg,
            'details': event_handler.ftpcmd
        }
        log_to_mongodb("ftp", client_ip, data)
    
    handler.on_file_sent = log_ftp_activity
    handler.on_file_received = log_ftp_activity
    handler.on_incomplete_file_sent = log_ftp_activity
    handler.on_incomplete_file_received = log_ftp_activity
    handler.on_login = lambda event_handler: log.info(f"Login from {event_handler.remote_ip}")
    handler.on_disconnect = lambda event_handler: log.info(f"Disconnected: {event_handler.remote_ip}")
    
    server = FTPServer(("0.0.0.0", 2121), handler)
    log.info("FTP server is running on port 2121")
    server.serve_forever()

if __name__ == '__main__':
    log.info(msg='Starting the Honeypot')
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    ssh_thread = threading.Thread(target=start_ssh_server, daemon=True)
    ftp_thread = threading.Thread(target=start_ftp_server, daemon=True)

    http_thread.start()
    ssh_thread.start()
    ftp_thread.start()

    http_thread.join()
    ssh_thread.join()
    ftp_thread.join()