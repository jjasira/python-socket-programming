import socket

SERVER_IP = '127.0.0.1'  # Replace with your server's IP
SERVER_PORT = 12345  # Replace with your server's port

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((SERVER_IP, SERVER_PORT))

# Send data to the server
data = "Hello, server!"
client_socket.send(data.encode())

# Receive response from the server
response = client_socket.recv(1024)
print("Server response:", response.decode())

# Close the socket
client_socket.close()
