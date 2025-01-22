from flask import Flask, request
import logging
import socket

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

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
                client_socket.close()
    except Exception as e:
        log.error(f'SSH server error: {e}')
        return False


if __name__ == '__main__':
    log.info(msg='Starting the Honeypot')
    start_ssh_server()