"""Standard Library imports"""
import configparser
import logging
import re
import socket
import ssl
import threading
import time

"""module imports"""
"""These are the different file search algorithms that we can implement in our search function."""
from searchalgorithms import boyer_moore_search, kmp_search, naive_search, AhoCorasick, rabin_karp_search

"""Load configuration."""
config = configparser.ConfigParser()
config.read('config.ini')

"""Define constants from configuration."""
# LISTEN_IP: str = config.get('server', 'listen_ip')
LISTEN_IP = socket.gethostbyname(socket.gethostname())
# PORT: int = int(config.get('server', 'port'))
PORT = 5050
# SSL_ENABLED: bool = config.getboolean('server', 'ssl_enabled')
SSL_ENABLED= False
# CERTIFICATE_PATH: str = config.get('server', 'certificate_path')
# REREAD_ON_QUERY: bool = config.getboolean('server', 'reread_on_query')
REREAD_ON_QUERY = False
# FILE_PATH: str = config.get('server', 'linuxpath')
FILE_PATH = "200k.txt"
HEADER: int = 1024
FORMAT: str = "utf-8" 
DISCONNECT_MESSAGE: str = "!DISCONNECT"

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


"""Set up SSL context if enabled."""
context = None
if SSL_ENABLED:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(CERTIFICATE_PATH)

"""This function will help us read the file and store the result in string
    It will come in handy when we want to reread the file content.
"""
def read_file(file_path: str) -> str:
    """Open the file with reading previledges, 
        read the content and store in variable called file_content.
    """
    with open(file_path , 'r') as file:
        file_content = file.read()
    return file_content

"""This will be the file's content when the server is ran for the first time."""
Initial_file_content: str = read_file(FILE_PATH)

"""Check to see the file is not empty."""
if Initial_file_content is None:
    logging.error('File content not loaded!')

def search_string(msg: str, file_path: str) -> bool:
    """This function takes the string or pattern being searched and the file or text 
        to be searched and return True if it is found and False otherwise.
    """
    start: float = time.perf_counter() # Log when the function starts
    print(f'search query: {msg}')
    if REREAD_ON_QUERY  == False:
        """We will use the file as read when the server was started."""
        """We can implement any of our imported search methods, I have gone with the default
           python file search algorithm because it's the fastest.
        """
        """
            if kmp_search(Initial_file_content, msg) == -1:
                Found = False
            else:
                Found = True
        """
        Found: bool = re.search(rf'^{msg}$', Initial_file_content, re.MULTILINE) is not None
        finish: float = time.perf_counter() # Log when the function was finished
        print(f'finished in {round(finish-start, 2)} second(s)') # Get the total time spent on the search
        return Found
    else:
        file_content: str = read_file(file_path)  # Reload file on each query
        if file_content is None:
            logging.error('File content not loaded!')
            return False
        Found: bool = re.search(rf'^{msg}$', file_content, re.MULTILINE) is not None
        finish: float = time.perf_counter()
        print(f'finished in {round(finish-start, 2)} second(s)')
        return Found

"""Function to handle client requests"""
def handle_client(client_socket: socket) -> None:
    try:
        """Receive data from client in the required format and size in bytes"""
        connected: bool= True
        while connected:
            msg_length = client_socket.recv(HEADER).decode(FORMAT).rstrip('\x00')
            if msg_length:
                msg_length: int = int(msg_length)
                data: str = client_socket.recv(msg_length).decode(FORMAT).rstrip('\x00')
                if data == DISCONNECT_MESSAGE:
                    connected = False
                else:
                    found: bool = search_string(data, FILE_PATH) # Use the search method defined to search for the pattern
                    if found:
                        """Send message if the string is found."""
                        client_socket.send(b'STRING EXISTS\n')
                    else:
                        """Send message if the string is not found."""
                        client_socket.send(b'STRING NOT FOUND\n')
        
    except Exception as e:
        """Raise an exceotion if an error such as a disconnection occurs."""
        print(f'Exception occurred: {e}')
    
    finally:
        client_socket.close()

"""Main server loop"""
def main()-> None:
    """Set up server socket"""
    server_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((LISTEN_IP, PORT))
    server_socket.listen()

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
