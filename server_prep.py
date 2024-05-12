import socket
import ssl
import configparser
import threading
import os

"""Load configuration"""
config = configparser.ConfigParser()
config.read('config.ini')

"""Define constants from configuration"""
LISTEN_IP: int = config.get('server', 'listen_ip')
PORT: int = int(config.get('server', 'port'))
SSL_ENABLED: bool = config.getboolean('server', 'ssl_enabled')
CERTIFICATE_PATH: str = config.get('server', 'certificate_path')
REREAD_ON_QUERY: bool = config.getboolean('server', 'reread_on_query')
FILE_PATH: str = config.get('server', 'file_path')

"""Set up SSL context if enabled"""
context = None
if SSL_ENABLED:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERTIFICATE_PATH)

"""Function to handle client requests"""
def handle_client(client_socket) -> None:
    try:
        """Receive data from client in the required format and size in bytes"""
        data: str = client_socket.recv(1024).decode().rstrip('\x00')

        """Search for string in file"""
        with open(FILE_PATH, 'r') as file:
            found: bool = False
            for line in file:
                if data == line.strip():
                    found = True
                    break

        """Send response back to client"""
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
        print(f'Connection from {addr[0]}:{addr[1]}')

        if SSL_ENABLED:
            client_socket: socket = context.wrap_socket(client_socket, server_side=True)

        client_thread: threading = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == '__main__':
    main()
