import configparser
import socket
import ssl
import sys

# Load configuration.
config = configparser.ConfigParser()
config.read('config.ini')

SERVER_IP: str = config.get('server', 'listen_ip')
# SERVER_IP: str = socket.gethostbyname(socket.gethostname())
SERVER_PORT: int = int(config.get('server', 'port'))
# SERVER_PORT: int = 5050
SSL_ENABLED: bool = config.getboolean('server', 'ssl_enabled')
# SSL_ENABLED: bool = False
PEM_FILE_LOCATION: str = config.get('server', 'certificate_pem')
HEADER: int = 1024
DISCONNECT_MESSAGE: str = "!DISCONNECT"
ADDR: tuple = (SERVER_IP, SERVER_PORT)
FORMAT: str = "utf-8"

if SSL_ENABLED:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(PEM_FILE_LOCATION)

# Create a socket object.
client_socket: socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
if SSL_ENABLED:
    client_socket = context.wrap_socket(
        client_socket, server_hostname=SERVER_IP)
    client_socket.connect(ADDR)
else:
    client_socket.connect((SERVER_IP, SERVER_PORT))


def send_data(msg: str) -> None:
    """
    This function takes in a msg, encodes the message and sends it to the server

    :param msg: the message to be sent which will be passed as an argument when
    the client.py script is executed
    """
    message: bytes = msg.encode(FORMAT)
    msg_length: int = len(message)
    send_length: bytes = str(msg_length).encode(FORMAT)
    # Ensure that the message sent is the required size by padding or removing extra characters
    # this will also prevent BUFFER OVERFLOW
    send_length += b' ' * (HEADER - len(send_length))
    client_socket.send(send_length)
    client_socket.send(message)


# Send the message to the server
data: str = sys.argv[1]
send_data(data)

# Receive response from the server
response: bytes = client_socket.recv(1024)
print("Server response:", response.decode(FORMAT))
# Close the socket
client_socket.close()
