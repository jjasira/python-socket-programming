import configparser
import logging
import re
import socket
import ssl
import threading
import time

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Define constants from configuration
LISTEN_IP: str = config.get('server', 'listen_ip')
PORT: int = int(config.get('server', 'port'))
SSL_ENABLED: bool = config.getboolean('server', 'ssl_enabled')
REREAD_ON_QUERY: bool = config.getboolean('server', 'reread_on_query')
FILE_PATH: str = config.get('server', 'linuxpath')
HEADER: int = 1024
FORMAT: str = "utf-8"
DISCONNECT_MESSAGE: str = "!DISCONNECT"
CERTIFICATE_PATH: str = config.get('server', 'certificate_path')

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s')

# Set up SSL context if enabled
context = None
if SSL_ENABLED:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERTIFICATE_PATH)


def read_file(file_path: str) -> str:
    """
    This function will help us read the file and store the result in string
    It will come in handy when we want to reread the file content.

    :param file_path: The path to the file we will read from
    :return: A string of the file contents
    """
    with open(file_path, 'r') as file:
        file_content: str = file.read()
    return file_content


# This will be the file's content when the server is ran for the first time.
Initial_file_content: str = read_file(FILE_PATH)

# Check to see the file is not empty.
if Initial_file_content is None:
    logging.error('File content not loaded!')


def search_string(msg: str, file_path: str) -> bool:
    """This function takes the string or pattern being searched and the file or text
        to be searched and return True if it is found and False otherwise.

        :param msg: This is the message to be searched for
        :param file_path: This is the path to the file to be searched
    """
    start: float = time.perf_counter()  # Log when the function starts
    print(f'search query: {msg}')
    if not REREAD_ON_QUERY:
        # We will use the file as read when the server was started."""
        Found: bool = re.search(
            rf'^{msg}$',
            Initial_file_content,
            re.MULTILINE) is not None
        finish: float = time.perf_counter()  # Log when the function was finished
        # Get the total time spent on the search
        print(f'finished in {round(finish-start, 2)} second(s)')
        return Found
    else:
        file_content: str = read_file(file_path)  # Reload file on each query
        if file_content is None:
            logging.error('File content not loaded!')
            return False
        Found: bool = re.search(
            rf'^{msg}$',
            Initial_file_content,
            re.MULTILINE) is not None
        finish: float = time.perf_counter()
        print(f'finished in {round(finish-start, 2)} second(s)')
        return Found


def handle_client(client_socket: socket.socket) -> None:
    """Function to handle client requests

       :param client_socket: this is the socket that has requested to connect
    """
    try:
        # Receive data from client in the required format and size in bytes
        connected: bool = True
        while connected:
            msg_length: str = client_socket.recv(
                HEADER).decode(FORMAT).rstrip('\x00')
            if msg_length:
                msg_length: int = int(msg_length)
                data: str = client_socket.recv(
                    msg_length).decode(FORMAT).rstrip('\x00')
                if data == DISCONNECT_MESSAGE:
                    connected = False
                else:
                    # Use the search method defined to search for the pattern
                    found: bool = search_string(data, FILE_PATH)
                    if found:
                        client_socket.send(b'STRING EXISTS\n')
                    else:
                        client_socket.send(b'STRING NOT FOUND\n')
    except Exception as e:
        # Raise an exceotion if an error such as a disconnection occurs."""
        print(f'Exception occurred: {e}')
    finally:
        client_socket.close()


def main() -> None:
    """Main server loop"""
    # Set up server socket
    server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LISTEN_IP, PORT))
    server_socket.listen(5)
    if SSL_ENABLED:
       # The wrap_socket wrapper encrypts and decrypts the data going over
        # the soxket with SSL.
        server_socket: socket = context.wrap_socket(
            client_socket, server_side=True)

    print(f'Server listening on {LISTEN_IP}:{PORT}')

    # Accept incoming connections and spawn threads
    while True:
        client_socket, addr = server_socket.accept()
        print(f'Connection from {addr[0]}:{addr[1]}')
        client_thread: threading = threading.Thread(
            target=handle_client, args=(client_socket,))
        client_thread.start()


if __name__ == '__main__':
    main()
