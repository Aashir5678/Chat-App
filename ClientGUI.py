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
        self.parent.geometry("200x80")
        self.parent.resizable(False, False)
        self.parent.title("Chat App")
        self.ON_CLOSE = "WM_DELETE_WINDOW"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.connected_clients = []
        self.messages = []
        self.client = None

        self.UsernameLabel = tk.Label(self.parent, text="Username:", font=("Comic Sans", 15, "bold"))
        self.UsernameEntry = tk.Entry(self.parent)
        self.ChatListbox = None
        self.ChatText = None
        self.ClientsListbox = None

        self.UsernameEntry.bind("<Return>", lambda event: self.make_client(self.UsernameEntry.get()))

        self.parent.protocol(self.ON_CLOSE, self.quit)

        self.UsernameLabel.pack()
        self.UsernameEntry.pack()

        self.parent.iconify()
        self.parent.update()
        self.parent.deiconify()

    def make_client(self, username):
        """
        Makes a client
        :param username: str
        """
        if username:
            self.create_client(username)

            for widget in self.parent.winfo_children():
                widget.destroy()

            self.parent.geometry("500x700")
            self.ChatListbox = tk.Listbox(self.parent, height=30, width=80)
            self.ChatText = tk.Text(self.parent, width=50, height=1)

            self.ChatListbox.insert(tk.END, f"{self.client.username} has joined the chat !")

            self.ChatText.bind("<Return>", lambda event: self.send_message(self.ChatText.get("1.0", tk.END)))
            for client in self.get_clients():
                self.ChatListbox.insert(tk.END, client.username)

            self.ChatListbox.pack()
            self.ChatText.pack()

    def send_message(self, message):
        """Sends a message to the server"""
        message = message.strip("\n")
        self.ChatListbox.insert(tk.END, f"{self.client.username}: {message}")
        self.client.send_message(message)
        self.ChatText.delete("1.0", tk.END)

    def create_client(self, username):
        """Creates a client with the username provided"""
        self.client = Client(username)
        self.client.connect()
        for client_info in self.client.all_client_info:
            for message in client_info.messages:
                self.messages.append(f"{client_info.username}: {message}")

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
