import threading
import tkinter as tk
from server import Server
from client import Client


class App:
    def __init__(self, parent):
        """
        :param parent: tk.Tk
        """
        self.parent = parent
        self.parent.geometry("300x240")
        self.parent.resizable(True, False)
        self.parent.title("Chat App")
        self.ON_CLOSE = "WM_DELETE_WINDOW"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.connected_clients = []
        self.messages = []
        self.client = None

        self.UsernameLabel = tk.Label(self.parent, text="Username:", font=("Comic Sans", 15, "bold"))
        self.UsernameEntry = tk.Entry(self.parent)
        self.PasswordLabel = tk.Label(self.parent, text="Server password:", font=("Comic Sans", 15, "bold"))
        self.PasswordEntry = tk.Entry(self.parent)
        self.PortLabel = tk.Label(self.parent, text="Port:", font=("Comic Sans", 15, "bold"))
        self.PortEntry = tk.Entry(self.parent)
        self.HostLabel = tk.Label(self.parent, text="Server host:", font=("Comic Sans", 15, "bold"))
        self.HostEntry = tk.Entry(self.parent)
        self.JoinChatButton = tk.Button(self.parent, text="Join Chat", padx=10, pady=10)

        self.PortEntry.insert(0, "5050")
        self.HostEntry.insert(0, "localhost")

        self.PasswordEntry.config(show="*")
        self.ChatListbox = None
        self.ChatText = None
        self.ClientsListbox = None
        self.messages_thread = None

        self.JoinChatButton.bind("<Button-1>", lambda event: self.make_client(self.UsernameEntry.get(),
                                                                              self.PasswordEntry.get(),
                                                                              self.PortEntry.get(),
                                                                              self.HostEntry.get()
                                                                              ))

        self.parent.protocol(self.ON_CLOSE, self.quit)

        self.UsernameLabel.pack()
        self.UsernameEntry.pack()
        self.PasswordLabel.pack()
        self.PasswordEntry.pack()
        self.PortLabel.pack()
        self.PortEntry.pack()
        self.HostLabel.pack()
        self.HostEntry.pack()
        self.JoinChatButton.pack()

        self.parent.iconify()
        self.parent.update()
        self.parent.deiconify()

    def make_client(self, username, password, port, host):
        """
        Makes a client
        :param username: str
        :param host: str
        :returns: None
        """
        if username:
            connected = self.create_client(username, password, port, host)

            if not connected:
                return

            for widget in self.parent.winfo_children():
                widget.destroy()

            self.parent.geometry("500x700")
            self.ChatListbox = tk.Listbox(self.parent, height=30, width=80)
            self.ChatText = tk.Text(self.parent, width=50, height=1)
            self.UsernameLabel = tk.Label(self.parent, text=f"{username}: ")

            self.ChatText.bind("<Return>", lambda event: self.send_message(self.ChatText.get("1.0", tk.END)))
            for client in self.get_all_client_info():
                self.ChatListbox.insert(tk.END, client.username)

            self.ChatListbox.pack()
            self.ChatText.pack()

            username_label_x = 31

            username_label_x -= len(username) * 5
            self.UsernameLabel.place(x=username_label_x, y=484)

            self.get_messages()

    def get_messages(self):
        """
        Gets the messages from every client and displays them in the ChatListbox
        :returns: None
        """
        for client_info in self.client.all_client_info:
            if len(client_info.messages) == 1:
                join_message = client_info.messages[0]

                if join_message not in self.messages:
                    self.messages.append(join_message)

            else:
                for message_index in range(-1, len(client_info.messages) - 1):
                    if message_index:
                        message = client_info.messages[message_index]

                        if message == self.DISCONNECT_MESSAGE:
                            print ("disconnecting")
                            message = f"{client_info.username} has disconnected !"

                        else:
                            message = f"{client_info.username}: {message}"

                        if message not in self.messages:
                            self.messages.append(message)

        self.ChatListbox.delete(0, tk.END)
        for message in self.messages:
            self.ChatListbox.insert(tk.END, message)

        self.parent.after(50, self.get_messages)

    def send_message(self, message):
        """
        Sends a message to the server
        :param message: str
        :returns: None
        """
        message = message.strip("\n")
        if message != self.DISCONNECT_MESSAGE:
            self.messages.append(f"{self.client.username}: {message}")
            self.ChatListbox.insert(tk.END, f"{self.client.username}: {message}")

        else:
            self.messages.append(message)
            self.ChatListbox.insert(tk.END, f"{self.client.username} has disconnected !")

        self.client.send_message(message)
        self.ChatText.delete("1.0", tk.END)

    def create_client(self, username, password, port, host):
        """
        Creates a client with the username provided, returns True if client was successfully created
        :param username: str
        :param password: str
        :param port: str or int
        :param host: str
        :returns: bool
        """

        try:
            port = int(port)

        except ValueError:
            return

        if host == "localhost":
            self.client = Client(username, server_pass=password, port=port)

        else:
            self.client = Client(username, server_pass=password, port=port, server_machine=host)

        connect = self.client.connect()
        if connect:
            for client_info in self.client.all_client_info:
                if len(client_info.messages) == 1:
                    join_message = client_info.messages[0]

                    if join_message not in self.messages:
                        self.messages.append(join_message)

                else:
                    for message_index in range(-1, len(client_info.messages) - 1):
                        if message_index:
                            message = client_info.messages[message_index]
                            message = f"{client_info.username}: {message}"

                            if message not in self.messages:
                                self.messages.append(message)

            return True

        return False

    def get_all_client_info(self):
        """
        Gets all the connected clients info
        :returns: list[ClientInfo]
        """
        return self.client.all_client_info

    def quit(self):
        """
        Quits the connection to server, and the tk window
        :returns: None
        """
        if self.client is not None:
            self.send_message(self.DISCONNECT_MESSAGE)

        self.parent.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
