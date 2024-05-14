import socket
import ssl
import configparser
import threading
import re
import time
import logging



"""Load configuration"""
config = configparser.ConfigParser()
config.read('config.ini')

"""Define constants from configuration"""
LISTEN_IP: str = config.get('server', 'listen_ip')
PORT: int = int(config.get('server', 'port'))
SSL_ENABLED: bool = config.getboolean('server', 'ssl_enabled')
REREAD_ON_QUERY: bool = config.getboolean('server', 'reread_on_query')
FILE_PATH: str = config.get('server', 'linuxpath')
HEADER = 1024
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

"""Setup logging"""
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

"""Set up SSL context if enabled"""
context = None
if SSL_ENABLED:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERTIFICATE_PATH)

"""Function to read file content"""
def read_file(file_path) -> str:
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content

"""Initial file content"""
Initial_file_content = read_file(FILE_PATH)

if Initial_file_content is None:
    logging.error('File content not loaded!')

def search_string(msg: str, file_path) -> bool:
    start = time.perf_counter()
    print(f'search query: {msg}')
    if not REREAD_ON_QUERY:
        Found = re.search(rf'^{msg}$', Initial_file_content, re.MULTILINE) is not None
        finish = time.perf_counter()
        print(f'finished in {round(finish-start, 2)} second(s)')
        return Found
    else:
        file_content = read_file(file_path)
        if file_content is None:
            logging.error('File content not loaded!')
            return False
        finish = time.perf_counter()
        print(f'finished in {round(finish-start, 2)} second(s)')
        return re.search(rf'^{msg}$', file_content, re.MULTILINE) is not None

"""Function to handle client requests"""
def handle_client(client_socket: socket.socket) -> None:
    try:
        connected = True
        while connected:
            msg_length = client_socket.recv(HEADER).decode(FORMAT).rstrip('\x00')
            if msg_length:
                msg_length = int(msg_length)
                data = client_socket.recv(msg_length).decode(FORMAT).rstrip('\x00')
                if data == DISCONNECT_MESSAGE:
                    connected = False
                else:
                    found = search_string(data, FILE_PATH)
                    if found:
                        client_socket.send(b'STRING EXISTS\n')
                    else:
                        client_socket.send(b'STRING NOT FOUND\n')
    except Exception as e:
        print(f'Exception occurred: {e}')
    finally:
        client_socket.close()

"""Main server loop"""
def main() -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LISTEN_IP, PORT))
    server_socket.listen(5)

    print(f'Server listening on {LISTEN_IP}:{PORT}')

    while True:
        client_socket, addr = server_socket.accept()
        print(f'Connection from {addr[0]}:{addr[1]}')
        
        if SSL_ENABLED:
            client_socket = context.wrap_socket(client_socket, server_side=True)

        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    main()
