import threading
import tkinter as tk
from server import Server


class ServerGUI:
    """Represents a server GUI"""
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Server")
        self.ON_CLOSE = "WM_DELETE_WINDOW"

        self.server = None
        self.server_password = None
        self.PortLabel = tk.Label(self.parent, text="Port:")
        self.PortEntry = tk.Entry(self.parent)

        self.PasswordLabel = tk.Label(self.parent, text="Server password:")
        self.PasswordEntry = tk.Entry(self.parent)
        self.PasswordEntry.config(show="*")
        self.CreateServerButton = tk.Button(self.parent, text="Create Server")
        self.ClientsListbox = tk.Listbox(self.parent, height=30, width=30)
        self.IPLabel = tk.Label(self.parent)
        self.parent.protocol(self.ON_CLOSE, self.quit)

        self.PortLabel.pack()
        self.PortEntry.pack()
        self.PasswordLabel.pack()
        self.PasswordEntry.pack()
        self.CreateServerButton.pack()

        self.PortEntry.insert(0, "5050")
        self.server_thread = threading.Thread(target=self.make_server, args=(self.PortEntry.get(),))
        self.server_thread.daemon = True
        self.CreateServerButton.config(command=self.server_thread.start)

        self.parent.iconify()
        self.parent.update()
        self.parent.deiconify()

    def check_for_clients(self):
        """
        Checks for any new clients, and adds them to the clients listbox
        :return: None
        """
        self.ClientsListbox.delete(0, tk.END)

        for client in self.server.connected_clients:
            self.ClientsListbox.insert(tk.END, client.username)

        self.parent.after(100, self.check_for_clients)

    def make_server(self, port):
        """
        Sets up the server
        :param port: str or int
        :returns: None
        """
        try:
            port = int(port)

        except ValueError:
            return

        self.server_password = self.PasswordEntry.get()
        self.server = Server(port, password=self.server_password)

        self.PortEntry.destroy()
        self.PasswordEntry.destroy()
        self.CreateServerButton.destroy()

        self.PasswordLabel.config(text="Server password: " + (self.server_password if self.server_password else "No password"))
        self.IPLabel.config(text="Server IP: " + str(self.server.SERVER))

        # Make server password label bold if there is not server password
        if not self.server_password:
            pass

        self.PortLabel.config(text="Port: " + str(port))
        self.IPLabel.pack()
        self.ClientsListbox.pack()
        self.check_for_clients()

        self.server.start()

    def quit(self):
        """
        Quits the server and parent window
        :returns: None
        """
        self.parent.destroy()
        if self.server is not None:
            self.server.close()

        quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
