import socket
import threading
import ssl

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SSL_AUTHENTICATION = False
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('ssl.pem', 'private.key')


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True

    while connected:
        msg_length  = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False

            print(f"[{addr}] {msg}")
            """ send a message back to the client"""
            conn.send("Message received".encode(FORMAT))
    conn.close()


def start():
    
    
    if SSL_AUTHENTICATION:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as server:
            server.bind(ADDR)
            server.listen()
            print(f"[LISTENING] Server is listening on {SERVER}")
            with context.wrap_socket(server, server_side=True) as ssock:
                while True:
                    conn, addr = ssock.accept()
                    thread = threading.Thread(target=handle_client, args=(conn, addr))
                    thread.start()
                    print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
    else:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(ADDR)
        server.listen()
        print(f"[LISTENING] Server is listening on {SERVER}")
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
start()

