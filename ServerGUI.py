import threading
import tkinter as tk
from server import Server


class ServerGUI:
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

        self.ClientsListbox = tk.Listbox(self.parent, height=30, width=30)
        self.ReloadButton = tk.Button(self.parent, text="Reload", command=self.reload)

        self.parent.protocol(self.ON_CLOSE, self.quit)

        self.PortLabel.pack()
        self.PortEntry.pack()
        self.PasswordLabel.pack()
        self.PasswordEntry.pack()

        self.PortEntry.insert(0, "5050")
        self.server_thread = threading.Thread(target=self.make_server, args=(self.PortEntry.get(),))
        self.server_thread.daemon = True
        self.parent.bind("<Return>", lambda event: self.run_thread())

        self.parent.iconify()
        self.parent.update()
        self.parent.deiconify()

    def run_thread(self):
        self.server_thread.start()

    def reload(self):
        self.ClientsListbox.delete(0, tk.END)

        for client in self.server.connected_clients:
            self.ClientsListbox.insert(tk.END, client.username)

        self.parent.after(100, self.reload)

    def make_server(self, port):
        """Makes the server"""
        try:
            port = int(port)

        except ValueError:
            return

        self.server_password = self.PasswordEntry.get()
        self.server = Server(port, password=self.server_password)

        self.PortEntry.destroy()
        self.PasswordEntry.destroy()

        self.PasswordLabel.config(text="Server password: " + (self.server_password if self.server_password else "No password"))

        self.PortLabel.config(text="Port: " + str(port))

        self.ClientsListbox.pack()
        self.ReloadButton.pack()
        self.reload()

        self.server.start()

    def quit(self):
        """Quits the server and parent window"""
        self.parent.destroy()
        if self.server is not None:
            self.server.close()

        quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerGUI(root)
    root.mainloop()
