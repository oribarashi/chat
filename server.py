import socket
import threading
import os

# Server configuration
HOST = '127.0.0.1'
PORT = 6666

# Create a server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server socket to the specified host and port
server.bind((HOST, PORT))

# Server starts listening for incoming connections
server.listen()

print('server listening to all connections.......')

# Lists to keep track of connected clients and their corresponding names
clients = []
names = []

# Function to send a message to all connected clients
def send_all(message):
    for client in clients:
        client.send(message)

# Function to handle communication with a connected client
def handle(client):
    while True:
        try:
            # Receive a message from the client
            message = client.recv(1024).decode('utf-8')
            header = message.split('+')[0]

            if message == 'online':
                # If client requests for the list of online users, send it
                x = "users+" + names.__repr__()
                client.send(x.encode('utf-8'))

            elif message == 'serverFiles':
                # If client requests for the server files, send the list
                x = "server files:+" + os.listdir(os.getcwd() + '/server_files').__repr__()
                client.send(x.encode('utf-8'))

            elif 'private' == header:
                # Handle private messages
                name, private_m = (message.split('+')[1], message.split('+')[2])
                name = name[0:len(name) - 1:]
                try:
                    ind = names.index(name)
                    to_client = clients[ind]
                    client.send(f"private to {name}{private_m[13 + len(names[clients.index(client)])::]}".encode())
                    to_client.send(private_m.encode("utf-8"))
                except (socket.error, ValueError, IndexError):
                    client.send(f"server: wrong name".encode('utf-8'))


            else:
                # Send any other message to all clients
                send_all(message.encode('utf-8'))

        except socket.error:
            # Handle client disconnection
            try:
                ind = clients.index(client)
                clients.remove(client)
                client.close()
                message1 = f"{names[ind]} left"
                send_all(message1.encode('utf-8'))
                name = names[ind]
                names.remove(name)
            except:
                client.close()

# Function to receive incoming client connections
def recieve():
    while True:
        client, address = server.accept()
        client.send("name".encode('utf-8'))
        name = client.recv(1024).decode('utf-8')

        # Notify all clients about the new connection
        send_all(f"{name} connected to the server\n".encode('utf-8'))

        names.append(str(name))
        clients.append(client)

        # Start a new thread to handle the communication with the connected client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

# Start receiving incoming client connections
recieve()