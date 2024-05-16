import ssl
import socket
import sys

SERVER_IP = socket.gethostbyname(socket.gethostname())  # Replace with your server's IP
SERVER_PORT = 5050  # Replace with your server's port
HEADER = 1024
DISCONNECT_MESSAGE: str = "!DISCONNECT"
SSL_ENABLED: bool = False
ADDR: tuple = (SERVER_IP, SERVER_PORT)
FORMAT = "utf-8"
PEM_FILE_LOCATION: str = "ssl.pem"

if SSL_ENABLED:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(PEM_FILE_LOCATION)

"""Create a socket object"""
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

"""Connect to the server"""
if SSL_ENABLED:
    client_socket = context.wrap_socket(client_socket, server_hostname=SERVER_IP)
    client_socket.connect(ADDR)
else:
    client_socket.connect((SERVER_IP, SERVER_PORT))

def send_data(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    """Ensure that the message sent is the required size by padding or removing extra characters
        this will also prevent BUFFER OVERFLOW
    """
    send_length += b' ' * (HEADER - len(send_length))
    client_socket.send(send_length)
    client_socket.send(message)
    """Receive response from the server"""

"""Send the message to the server""" 
data = sys.argv[1]
send_data(data)

response = client_socket.recv(1024)
print("Server response:", response.decode(FORMAT))
"""Close the socket"""
client_socket.close()
