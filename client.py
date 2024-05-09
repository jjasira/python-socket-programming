import socket
import ssl

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SSL_AUTHENTICATION = False
SERVER = socket.gethostbyname(socket.gethostname())

ADDR = (SERVER, PORT)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_verify_locations('ssl.pem')

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
"""We are connecting to our server"""
if SSL_AUTHENTICATION:
    client_soc = context.wrap_socket(client, server_hostname=SERVER)
    client_soc.connect(ADDR)
else:
    client.connect(ADDR)    


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

send("Hello world")
input()
send("Hello everyone")
input()
send("Hello James")


send(DISCONNECT_MESSAGE)

