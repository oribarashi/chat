import socket
import threading
import os
import RSA
import json

# Server configuration
HOST = socket.gethostbyname(socket.gethostname())
PORT = 6666

print(HOST)
primes = RSA.get_primes(15, 300)
PUBLIC_KEY, PRIVATE_KEY = RSA.keys(primes[0], primes[1])

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
keys = {}


# Function to send a message to all connected clients
def send_all(message):
    print(message)
    for client in clients:
        enc_message = RSA.encrypt(client['pub_k'], message)
        client['ip'].send(json.dumps(enc_message).encode())


# Function to handle communication with a connected client
def handle(client):
    while True:
        try:
            # Receive a message from the client
            message = json.loads(client.recv(1024).decode())
            enc_m = RSA.decrypt(PRIVATE_KEY, message)
            header = enc_m.split('+')[0]

            if enc_m == 'online':
                # If client requests for the list of online users, send it
                x = "users+" + names._repr_()
                client.send(x.encode('utf-8'))

            elif enc_m == 'serverFiles':
                # If client requests for the server files, send the list
                x = "server files:+" + os.listdir(os.getcwd() + '/server_files')._repr_()
                client.send(x.encode('utf-8'))

            elif 'private' == header:
                # Handle private messages
                name, private_m = (enc_m.split('+')[1], enc_m.split('+')[2])
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
                send_all(enc_m)

        except socket.error:
            # Handle client disconnection
            try:
                ind = clients.index(client)
                clients.remove(client)
                client.close()
                message1 = f"{names[ind]} left"
                send_all(message1)
                name = names[ind]
                names.remove(name)
            except:
                client.close()


# Function to receive incoming client connections
def recieve():
    while True:
        client, address = server.accept()
        start_dict = json.loads(client.recv(1024).decode())
        client.send(json.dumps(PUBLIC_KEY).encode())
        client_dict = {
            'name': start_dict['name'],
            'ip': client,
            'pub_k': start_dict['pub_k']
        }
        # Notify all clients about the new connection

        names.append(str(start_dict['name']))
        clients.append(client_dict)

        send_all(f"{start_dict['name']} connected to the server\n")

        # Start a new thread to handle the communication with the connected client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


# Start receiving incoming client connections
if __name__ == '__main__':
    recieve()
