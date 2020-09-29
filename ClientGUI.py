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
        self.parent.geometry("200x200")
        self.parent.resizable(False, False)
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

        self.PortEntry.insert(0, "5050")

        self.PasswordEntry.config(show="*")
        self.ChatListbox = None
        self.ChatText = None
        self.ClientsListbox = None
        self.messages_thread = None

        self.PortEntry.bind("<Return>", lambda event: self.make_client(self.UsernameEntry.get(),
                                                                           self.PasswordEntry.get(),
                                                                           self.PortEntry.get()
                                                                           ))

        self.PasswordEntry.bind("<Return>", lambda event: self.make_client(self.UsernameEntry.get(),
                                                                       self.PasswordEntry.get(),
                                                                       self.PortEntry.get()
                                                                       ))

        self.UsernameEntry.bind("<Return>", lambda event: self.make_client(self.UsernameEntry.get(),
                                                                       self.PasswordEntry.get(),
                                                                       self.PortEntry.get()
                                                                       ))

        self.parent.protocol(self.ON_CLOSE, self.quit)

        self.UsernameLabel.pack()
        self.UsernameEntry.pack()
        self.PasswordLabel.pack()
        self.PasswordEntry.pack()
        self.PortLabel.pack()
        self.PortEntry.pack()

        self.parent.iconify()
        self.parent.update()
        self.parent.deiconify()

    def make_client(self, username, password, port):
        """
        Makes a client
        :param username: str
        """
        if username:
            connected = self.create_client(username, password, port)

            if not connected:
                return

            for widget in self.parent.winfo_children():
                widget.destroy()

            self.parent.geometry("500x700")
            self.ChatListbox = tk.Listbox(self.parent, height=30, width=80)
            self.ChatText = tk.Text(self.parent, width=50, height=1)

            message = f"{self.client.username} has joined the chat !"
            self.ChatListbox.insert(tk.END, message)

            self.ChatText.bind("<Return>", lambda event: self.send_message(self.ChatText.get("1.0", tk.END)))
            for client in self.get_clients():
                self.ChatListbox.insert(tk.END, client.username)

            self.ChatListbox.pack()
            self.ChatText.pack()

            self.get_messages()

    def get_messages(self):
        """Gets the messages from every client and displays them in the ChatListbox"""
        self.messages.clear()

        for client_info in self.client.all_client_info:
            for message in client_info.messages:
                self.messages.append(f"{client_info.username}: {message}")

        self.ChatListbox.delete(0, tk.END)
        for message in self.messages:
            self.ChatListbox.insert(0, message)

        self.parent.after(100, self.get_messages)

    def send_message(self, message):
        """Sends a message to the server"""
        message = message.strip("\n")
        self.messages.insert(0, f"{self.client.username}: {message}")
        self.ChatListbox.insert(tk.END, f"{self.client.username}: {message}")
        self.client.send_message(message)
        self.ChatText.delete("1.0", tk.END)

    def create_client(self, username, password, port):
        """Creates a client with the username provided"""

        try:
            port = int(port)

        except ValueError:
            return

        self.client = Client(username, server_pass=password, port=port)
        connect = self.client.connect()
        if connect:
            for client_info in self.client.all_client_info:
                for message in client_info.messages:
                    self.messages.append(f"{client_info.username}: {message}")

            return True

        return False

    def get_clients(self):
        """
        Gets all the clients connected
        :returns: list[Client]
        """
        return self.connected_clients

    def quit(self):
        """Quits the connection to server"""
        if self.client is not None:
            self.client.send_message(self.DISCONNECT_MESSAGE)
            self.client.disconnect()

        self.parent.destroy()
        quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
