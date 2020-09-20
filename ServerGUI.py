import threading
import tkinter as tk
from server import Server


class ServerGUI:
    def __init__(self, parent):
        self.parent = parent
        self.parent.title("Server")
        self.ON_CLOSE = "WM_DELETE_WINDOW"

        self.server = None
        self.server_thread = threading.Thread(target=self.make_server)
        self.ServerLabel = tk.Label(self.parent)
        self.PortLabel = tk.Label(self.parent)
        self.ChatListbox = tk.Listbox(self.parent, height=30, width=80)

        self.parent.protocol(self.ON_CLOSE, self.quit)

        self.ServerLabel.pack()
        self.PortLabel.pack()
        self.server_thread.start()

        self.parent.iconify()
        self.parent.update()
        self.parent.deiconify()

    def make_server(self):
        """Makes the server"""
        self.server = Server()
        for client in self.server.connected_clients:
            self.ClientsListbox.insert(client.username)

        self.ServerLabel.config(text="Server has started...")
        self.PortLabel.config(text=f"Port: {self.server.PORT}")

        self.ChatListbox.pack()
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
