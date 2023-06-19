import socket  # Imports the socket library for network connections
import threading  # Imports the threading library for multi-threading
import tkinter  # Imports the tkinter library for GUI
import tkinter.scrolledtext  # Imports the scrolledtext module from tkinter for text area with a scrollbar
from tkinter import simpledialog  # Imports the simpledialog module from tkinter for easy dialogs

# Specifies the IP address and port of the server
HOST = '127.0.0.1'
PORT = 6666


# Defines the Client class
class Client:

    # Initializes the client object
    def __init__(self, port):
        # Creates a hidden root window for dialogs
        msg = tkinter.Tk()
        msg.geometry("50x50+400+100")  # Sets window geometry
        msg.withdraw()  # Hides the window

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
            except:
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

        self.logout_button = tkinter.Button(self.window, text="Logout", command=self.logout, padx=10, pady=5)
        self.logout_button.grid(row=0, column=0)

        self.list_button = tkinter.Button(self.window, text="online list", command=self.list_online, padx=10, pady=5)
        self.list_button.grid(row=0, column=1)

        self.files_button = tkinter.Button(self.window, text="server files", padx=20, pady=5, command=self.show_files)
        self.files_button.grid(row=0, column=2)

        self.clear_button = tkinter.Button(self.window, text="clear", command=self.clear, padx=2, pady=5)
        self.clear_button.grid(row=0, column=3)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.window, height=20, width=50)
        self.text_area.grid(row=2, column=1)
        self.text_area.config(state='disabled')

        self.to_label = tkinter.Label(self.window, text="To(blank to all)", bg="lightgray", padx=0.5, pady=1)
        self.to_label.config(font=("Ariel", 9))
        self.to_label.grid(row=6, column=0)

        self.to_input = tkinter.Text(self.window, height=1, width=15)
        self.to_input.grid(row=7, column=0)

        self.msg_label = tkinter.Label(self.window, text="Message", bg="lightgray", padx=0.5, pady=1)
        self.msg_label.config(font=("casual", 9))
        self.msg_label.grid(row=6, column=1)

        self.input = tkinter.Text(self.window, height=2, width=50)
        self.input.grid(row=7, column=1)

        self.send_button = tkinter.Button(self.window, text="send", command=self.write, padx=20, pady=5)
        self.send_button.grid(row=7, column=2)

        self.file_label = tkinter.Label(self.window, text="server file name", bg="lightgray", padx=0.5, pady=1)
        self.file_label.config(font=("casual", 9))
        self.file_label.grid(row=9, column=0)

        self.file_input = tkinter.Text(self.window, height=1, width=15)
        self.file_input.grid(row=10, column=0)

        self.save_label = tkinter.Label(self.window, text="save as", bg="lightgray", padx=0.5, pady=1)
        self.save_label.config(font=("casual", 9))
        self.save_label.grid(row=9, column=1)

        self.save_input = tkinter.Text(self.window, height=1, width=50)
        self.save_input.grid(row=10, column=1)

        self.proceed_button = tkinter.Button(self.window, text="proceed", command=self.proceed, padx=20, pady=5)
        self.proceed_button.grid(row=10, column=2)

        # Setting 'gui_done' as True to indicate that GUI has been set up
        self.gui_done = True

        # Binding the 'stop' function to the window close button
        self.window.protocol("WM_DELETE_WINDOW", self.stop)

        # Starting the main event loop of the tkinter window
        self.window.mainloop()

    # Defining the 'proceed' method. The implementation details are missing in the provided code.
    def proceed(self):
        pass

    # Defining the 'stop' method which stops the client, destroys the GUI and closes the socket connection
    def stop(self):
        self.running = False  # Stop the client
        self.window.destroy()  # Destroy the GUI
        self.sock.close()  # Close the socket
        exit(0)  # Exit the program

    # Defining the 'logout' method which performs the same steps as 'stop'
    def logout(self):
        self.running = False
        self.window.destroy()
        self.sock.close()
        exit(0)

    # Defining the 'show_files' method which sends a message to the server requesting the server's files
    def show_files(self):
        message = "serverFiles"
        self.sock.send(message.encode('utf-8'))  # Send the message to the server

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
            self.sock.send(message.encode('utf-8'))
        # If the 'to_input' field is not empty, the message is a private message to a specific client
        else:
            private_m = f"private+{self.to_input.get('1.0', 'end')}+private from {self.name}:{self.input.get('1.0', 'end')}"
            self.sock.send(private_m.encode('utf-8'))
        self.input.delete('1.0', 'end')  # Clear the input field

    # Defining the 'receive' method which continuously listens for incoming messages
    # Defining the 'receive' method which continuously listens for incoming messages from the server
    def receive(self):
        # Continuously receive messages as long as the client is running
        while self.running:
            try:
                # Receive a message from the server
                message = self.sock.recv(1024).decode('utf-8')
                # Parse the header from the received message
                header = message.split('+')[0]

                # If the server is asking for the client's name
                if message == 'name':
                    # Send the client's name to the server
                    self.sock.send(self.name.encode('utf-8'))

                # If the server is sending the list of online users
                elif 'users' == header:
                    # Create a new window to display the online users
                    online_window = tkinter.Toplevel(self.window)
                    online_window.geometry("172x120+400+100")
                    online_window.title("online")
                    online_window.configure(bg="lightblue")

                    # Display the list of online users in the new window
                    tkinter.Label(online_window, bg="lightblue", text="users: " + message.split('+')[1],
                                  wraplength=130).pack()

                # If the server is sending the list of files
                elif 'server files:' == header:
                    # Create a new window to display the server's files
                    online_window2 = tkinter.Toplevel(self.window)
                    online_window2.geometry("172x120+400+100")
                    online_window2.title("server files")
                    online_window2.configure(bg="lightblue")

                    # Display the server's files in the new window
                    tkinter.Label(online_window2, bg="lightblue", text="server files: " + message.split('+')[1],
                                  wraplength=130).pack()

                # If the received message is anything else
                else:
                    # If the GUI has been set up
                    if self.gui_done:
                        # Enable editing in the text area
                        self.text_area.config(state='normal')

                        # Append the received message to the text area
                        self.text_area.insert('end', message)

                        # Automatically scroll to the end of the text area
                        self.text_area.yview('end')

                        # Disable editing in the text area
                        self.text_area.config(state='disabled')

            # If an exception occurs while receiving messages
            except:
                # Break the loop
                break

    # Instantiate a client object and connect to the server


client = Client(PORT)
