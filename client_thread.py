import socket  # Imports the socket library for network connections
import threading  # Imports the threading library for multi-threading
import tkinter as tk  # Imports the tkinter library for GUI
import tkinter.scrolledtext  # Imports the scrolledtext module from tkinter for text area with a scrollbar
from tkinter import simpledialog  # Imports the simpledialog module from tkinter for easy dialogs
import sys
import RSA
import json

# Specifies the IP address and port of the server
HOST = socket.gethostbyname(socket.gethostname())
PORT = 6666
BUFFER = 4096


# Defines the Client class
class Client:
    # Initializes the client object
    def __init__(self, port):

        self.primes = RSA.get_primes(15, 300)
        self.pub_k, self.priv_k = RSA.keys(self.primes[0], self.primes[1])
        self.server_public_key = None
        # Creates a hidden root window for dialogs
        msg = tkinter.Tk()
        msg.geometry("50x50+400+100")  # Sets window geometry
        msg.withdraw()  # Hides the window
        msg.resizable(False, False)

        # Creates dialogs to get the client's name and the server IP
        self.name = simpledialog.askstring("Name", "Enter your name", parent=msg)
        self.serverIp = simpledialog.askstring("ServerIP", "Enter server ip(exp 10.0.0.4):", parent=msg)
        self.sock = None  # Initialises the socket to None

        # Tries to connect to the server
        while self.sock is None and self.serverIp != 'exit':
            try:
                host = self.serverIp
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creates a TCP/IP socket
                self.sock.connect((host, port))  # Connects the socket to the port where the server is listening
                start_m = {
                    'name': self.name,
                    'pub_k': self.pub_k
                }

                self.sock.send(json.dumps(start_m).encode())
                self.server_public_key = json.loads(self.sock.recv(BUFFER).decode())
                print(self.server_public_key)

            except ConnectionRefusedError:
                # If connection fails, ask for correct IP again or give option to exit
                self.serverIp = simpledialog.askstring("ServerIP",
                                                       "IP WAS NOT CORRECT PLZ TRY AGAIN\n write exit for stopping",
                                                       parent=msg)
                self.sock = None  # Reset the socket to None

        # If serverIp is 'exit', terminate the program
        if self.serverIp == 'exit':
            exit(0)

        msg.destroy()  # Destroys the hidden root window

        # Initializes some more attributes
        self.gui_done = False  # GUI is not done yet
        self.running = True  # Client is running

        # Creates threads for the GUI and for receiving data
        gui_thread = threading.Thread(target=self.gui_loop)
        recieve_thread = threading.Thread(target=self.receive)

        # Starts the threads
        gui_thread.start()
        recieve_thread.start()

    # Defines the method to create the GUI
    def gui_loop(self):
        # In this method, all the GUI elements (buttons, labels, text fields, etc.) are created and placed in the window.
        self.window = tkinter.Tk()
        self.window.geometry("690x480+400+100")
        self.window.title(self.name)
        self.window.configure(bg="lightgreen")

        self.logout_button = tk.Button(self.window, text="Logout", command=self.logout, padx=10, pady=5)
        self.logout_button.grid(row=0, column=0)

        self.list_button = tk.Button(self.window, text="online list", command=self.list_online, padx=10, pady=5)
        self.list_button.grid(row=0, column=1)

        self.clear_button = tk.Button(self.window, text="clear", command=self.clear, padx=2, pady=5)
        self.clear_button.grid(row=0, column=3)

        self.text_area = tk.scrolledtext.ScrolledText(self.window, height=20, width=50)
        self.text_area.grid(row=2, column=1)
        self.text_area.config(state='disabled')

        self.to_label = tk.Label(self.window, text="To(blank to all)", bg="lightgray", padx=0.5, pady=1)
        self.to_label.config(font=("Ariel", 9))
        self.to_label.grid(row=6, column=0)

        self.to_input = tk.Text(self.window, height=1, width=15)
        self.to_input.grid(row=7, column=0)

        self.msg_label = tk.Label(self.window, text="Message", bg="lightgray", padx=0.5, pady=1)
        self.msg_label.config(font=("casual", 9))
        self.msg_label.grid(row=6, column=1)

        self.input = tk.Text(self.window, height=2, width=50)
        self.input.grid(row=7, column=1)

        self.send_button = tk.Button(self.window, text="send", command=self.write, padx=20, pady=5)
        self.send_button.grid(row=7, column=2)


        # Setting 'gui_done' as True to indicate that GUI has been set up
        self.gui_done = True

        # Binding the 'stop' function to the window close button
        self.window.protocol("WM_DELETE_WINDOW", self.stop)

        # Starting the main event loop of the tk window
        self.window.mainloop()

    # Defining the 'proceed' method. The implementation details are missing in the provided code.
    def proceed(self):
        pass

    def stop(self):
        sys.exit()

    # Defining the 'logout' method which performs the same steps as 'stop'
    def logout(self):
        self.sock.close()
        sys.exit()

    # Defining the 'list_online' method which sends a message to the server requesting the list of online clients
    def list_online(self):
        message = "online"
        self.sock.send(message.encode('utf-8'))

    # Defining the 'clear' method which clears the text from the text area in the GUI
    def clear(self):
        self.text_area.config(state='normal')  # Enable editing in the text area
        self.text_area.delete('1.0', 'end')  # Delete all text in the text area
        self.text_area.config(state='disabled')  # Disable editing in the text area

    # Defining the 'write' method which sends a message to the server
    def write(self):
        # Checking if the 'to_input' field is empty, indicating a message to all clients
        if self.to_input.compare('end-1c', '==', '1.0'):
            message = f"{self.name}:{self.input.get('1.0', 'end')}"
            enc_message = RSA.encrypt(self.server_public_key, message)
            self.sock.send(json.dumps(enc_message).encode('utf-8'))
        # If the 'to_input' field is not empty, the message is a private message to a specific client
        else:
            private_m = f"private+{self.to_input.get('1.0', 'end')}+private from {self.name}:{self.input.get('1.0', 'end')}"
            enc_message = RSA.encrypt(self.server_public_key, private_m)
            self.sock.send(json.dumps(enc_message).encode('utf-8'))
        self.input.delete('1.0', 'end')  # Clear the input field

    # Defining the 'receive' method which continuously listens for incoming messages
    def receive(self):
        # Continuously receive messages as long as the client is running
        while self.running:
            try:
                # Receive a message from the server
                message = json.loads(self.sock.recv(BUFFER).decode())
                # Parse the header from the received message
                dec_m = RSA.decrypt(self.priv_k, message)
                print(dec_m)
                header = dec_m.split('+')[0]

                # If the server is sending the list of online users
                if header == 'users':
                    # Create a new window to display the online users
                    online_window = tk.Toplevel(self.window)
                    online_window.geometry("172x120+400+100")
                    online_window.title("online")
                    online_window.configure(bg="lightblue")

                    # Display the list of online users in the new window
                    tk.Label(online_window, bg="lightblue", text="users: " + message.split('+')[1],
                             wraplength=130).pack()

                # If the server is sending the list of files
                elif header == 'server files:':
                    # Create a new window to display the server's files
                    online_window2 = tk.Toplevel(self.window)
                    online_window2.geometry("172x120+400+100")
                    online_window2.title("server files")
                    online_window2.configure(bg="lightblue")

                    # Display the server's files in the new window
                    tk.Label(online_window2, bg="lightblue", text="server files: " + message.split('+')[1],
                             wraplength=130).pack()

                # If the received message is anything else
                else:
                    # If the GUI has been set up
                    if self.gui_done:
                        # Enable editing in the text area
                        self.text_area.config(state='normal')

                        # Append the received message to the text area
                        self.text_area.insert('end', f'{dec_m}\n')

                        # Automatically scroll to the end of the text area
                        self.text_area.yview('end')

                        # Disable editing in the text area
                        self.text_area.config(state='disabled')

            # If an exception occurs while receiving messages
            except Exception as E:
                print(f'Exeption {E} accured while running')
                # Break the loop
                break

    # Instantiate a client object and connect to the server


if __name__ == '__main__':
    client = Client(PORT)