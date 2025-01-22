from flask import Flask, request
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    log.info(msg='Starting the Honeypot')