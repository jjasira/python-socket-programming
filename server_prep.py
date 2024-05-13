import socket
import ssl
import configparser
import threading
import time


"""Load configuration"""
config = configparser.ConfigParser()
config.read('config.ini')

"""Define constants from configuration"""
# LISTEN_IP: int = config.get('server', 'listen_ip')
LISTEN_IP = socket.gethostbyname(socket.gethostname())
# PORT: int = int(config.get('server', 'port'))
PORT = 5050
# SSL_ENABLED: bool = config.getboolean('server', 'ssl_enabled')
SSL_ENABLED= False
# CERTIFICATE_PATH: str = config.get('server', 'certificate_path')
# REREAD_ON_QUERY: bool = config.getboolean('server', 'reread_on_query')
REREAD_ON_QUERY = False
# FILE_PATH: str = config.get('server', 'file_path')
FILE_PATH = "200k.txt"
HEADER: int = 1024
FORMAT: str = "utf-8" 
DISCONNECT_MESSAGE: str = "!DISCONNECT"

"""Set up SSL context if enabled"""
context = None
if SSL_ENABLED:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERTIFICATE_PATH)

def search_string(msg: str, file_path: str) -> bool:
    start = time.perf_counter()
    print(f'search query: {msg}')
    with open(file_path, 'r') as file:
        found: bool = False
        for line in file:
            if msg == line.strip():
                found = True
                break
    finish = time.perf_counter()
    print(f'finished in {round(finish-start, 2)} second(s)')
    return found


"""Function to handle client requests"""
def handle_client(client_socket: socket) -> None:
    try:
        """Receive data from client in the required format and size in bytes"""
        # data: str = client_socket.recv(HEADER).decode().rstrip('\x00')
        # print(data)

        connected: bool= True
        while connected:
            msg_length = client_socket.recv(HEADER).decode(FORMAT).rstrip('\x00')
            if msg_length:
                msg_length = int(msg_length)
                data = client_socket.recv(msg_length).decode(FORMAT).rstrip('\x00')
                if data == DISCONNECT_MESSAGE:
                    connected = False
                else:
                    found: bool = search_string(data, FILE_PATH)
                    if found:
                        """Send message if the string is found"""
                        client_socket.send(b'STRING EXISTS\n')
                    else:
                        """Send message if the string is not found"""
                        client_socket.send(b'STRING NOT FOUND\n')
        
    except Exception as e:
        """Raise an exceotion if the string is not found"""
        print(f'Exception occurred: {e}')
    
    finally:
        client_socket.close()

"""Main server loop"""
def main()-> None:
    """Set up server socket"""
    server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LISTEN_IP, PORT))
    server_socket.listen(5)

    print(f'Server listening on {LISTEN_IP}:{PORT}')

    """Accept incoming connections and spawn threads"""
    while True:
        client_socket, addr = server_socket.accept()
        print('[DEBUG]')
        print(f'Connection from {addr[0]}:{addr[1]}')
        

        if SSL_ENABLED:
            client_socket: socket = context.wrap_socket(client_socket, server_side=True)

        client_thread: threading = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    main()
