import socket
import threading
import time
import pytest
"""we will import the clone of our original server that will be used for testing purposes
   we will also import the required contants that will be used to format our messages
"""
from server_clone import main as server_main, DISCONNECT_MESSAGE, HEADER, FORMAT, LISTEN_IP, PORT

@pytest.fixture(scope='module')
def server():
    server_thread = threading.Thread(target=server_main, daemon=True)
    server_thread.start()
    """we will give our server some time to start"""
    time.sleep(1)
    yield
    """Server will be stopped when tests are done due to daemon=True"""

def send_message(sock: socket, message: str) -> None:
    message = message.encode(FORMAT)
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    sock.send(send_length)
    sock.send(message)

@pytest.mark.parametrize("input_string, expected_response", [
    ("TestString", b'STRING EXISTS\n'),  # Exists in file
    ("NonExistentString", b'STRING NOT FOUND\n'),  # Does not exist in file
    ("String", b'STRING NOT FOUND\n'), # The server should not return true for a word that is a substring
    ("tESTsTRING", b'STRING NOT FOUND\n'), # The query should be case sensitive
    ("Father", b'STRING NOT FOUND\n'), # Has single quotes at the end
    ("Mother", b'STRING EXISTS\n'), # The string is at the end of the file
    ("Brother", b'STRING EXISTS\n'), # The string is in the middle of the file
])
def test_server_responses(server, input_string: str, expected_response: str):
    host = LISTEN_IP
    port = PORT

    with socket.create_connection((host, port)) as sock:
        send_message(sock, input_string)
        response = sock.recv(HEADER)
        assert response == expected_response

def test_disconnect_message(server):
    host = LISTEN_IP
    port = PORT

    with socket.create_connection((host, port)) as sock:
        send_message(sock, DISCONNECT_MESSAGE)
        response = sock.recv(HEADER)
        assert response == b''
