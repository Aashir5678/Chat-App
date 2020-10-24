import socket
import threading
import pickle
from client import Client, ClientInfo


class Server:
    """Represents a server that holds clients"""
    HEADER = 2048

    def __init__(self, port=5050, password=""):
        self.PORT = port
        self.password = password
        self.HEADER = 2048
        self.FORMAT = "utf-8"
        self.SUCCESS = b"SUCCESSFUL CONNECTION"
        self.FAIL = b"FAILED CONNECTION"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER = socket.gethostbyname(socket.gethostname())
        self.connected_clients = []
        self.connections = []
        self.all_client_info = []
        self.ADDR = (self.SERVER, self.PORT)
        self.closed = False

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server.bind(self.ADDR)
        self.server.listen(5)

        print ("server has started...")
        while not self.closed:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn,))
            thread.daemon = True
            thread.start()

    def handle_client(self, conn):
        client, connection_status = self.create_client(conn)

        print (time.time())
        conn.send(connection_status)
        if connection_status == self.FAIL:
            return

        print ("connection status: " + str(connection_status))

        while client.connected:
            try:
                message_len = self.receive_message(conn)

            except ConnectionResetError:
                client.connected = False
                break

            if message_len:
                message_len = int(message_len)
                message = self.receive_message(conn, size=message_len)
                if message == self.DISCONNECT_MESSAGE:
                    break

                elif message is None:
                    continue

                print (f"{client.username}: {message}")
                self.connected_clients.remove(client)
                client_info = self.make_client_info(client)
                self.all_client_info.remove(client_info)

                send = pickle.dumps(client_info)
                for connection in self.connections:
                    connection.send("UPDATE CLIENT INFO".encode(self.FORMAT))
                    connection.send(send)

                client.messages.append(message)
                self.connected_clients.append(client)
                client_info = self.make_client_info(client)
                self.all_client_info.append(client_info)

                send = pickle.dumps(client_info)
                for connection in self.connections:
                    connection.send(send)

        disconnect_message = f"{client.username} has disconnected !"
        client.messages.append(disconnect_message)
        self.connected_clients.remove(self.make_client_info(client))
        client_info = self.make_client_info(client)
        self.all_client_info.remove(client_info)
        self.connections.remove(conn)

    def create_client(self, conn):
        message_len = self.receive_message(conn)
        password = ""
        if message_len:
            message_len = int(message_len)
            password = self.receive_message(conn, size=message_len)

        if password != self.password:
            print ("pass")
            return None, self.FAIL

        message_len = self.receive_message(conn)
        if message_len:
            message_len = int(message_len)
            username = self.receive_message(conn, size=message_len)

        else:
            print ("username")
            return None, self.FAIL

        client = Client(username, connected=True)
        client_info = self.make_client_info(client)

        self.all_client_info.append(client_info)
        self.connected_clients.append(client)

        all_client_info = pickle.dumps(self.all_client_info)
        conn.send(all_client_info)
        conn.send(pickle.dumps(None))

        join_message = client.username + " has joined the chat !"
        client_info.messages.append(join_message)

        for connection in self.connections:
            client_info = pickle.dumps(client_info)
            connection.send("NEW CLIENT".encode(self.FORMAT))
            connection.send(client_info)

        self.connections.append(conn)

        return client, self.SUCCESS

    def make_client_info(self, client):
        username = client.username
        messages = client.messages
        port = client.PORT
        server_machine = client.server_machine
        connected = client.connected

        return ClientInfo(username, messages, port=port, server_machine=server_machine, connected=connected)

    def receive_message(self, conn, size=HEADER, decode=True):
        if decode:
            message = conn.recv(size).decode(self.FORMAT)

        else:
            message = conn.recv(size)
        return message

    def close(self):
        self.server.close()

    def __repr__(self):
        return f"Server on {self.PORT}"


if __name__ == "__main__":
    server = Server()
    server.start()
