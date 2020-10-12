import socket
import pickle
import threading


class Client:
    HEADER = 2048
    """Represents a client on the server"""
    def __init__(self, username, port=5050, server_machine=socket.gethostname(), server_pass="", connected=False):
        self.PORT = port
        self.HEADER = 2048
        self.username = username
        self.server_password = server_pass
        self.FORMAT = "utf-8"
        self.SUCCESS = "SUCCESSFUL CONNECTION"
        self.FAIL = "FAILED CONNECTION"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.server_machine = server_machine
        self.get_clients_thread = threading.Thread(target=self.update_all_clients)

        try:
            self.socket = socket.gethostbyname(self.server_machine)

        except socket.error:
            raise TypeError("Server machine does not exist")

        self.connected = connected
        self.messages = []
        self.client_info = self.make_client_info(self)
        self.all_client_info = [self.client_info]

        self.ADDR = (self.socket, self.PORT)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client.connect(self.ADDR)
        self.connected = True
        self.send_message(self.server_password, save_message=False)
        self.send_message(self.username, save_message=False)

        data = []

        while True:
            client_info = self.client.recv(self.HEADER)

            try:
                status = client_info.decode(self.FORMAT)

            except UnicodeDecodeError:
                data.append(client_info)
                continue

            if status == "SEND COMPLETE":
                break

        self.all_client_info = pickle.loads(b"".join(data))
        connection_status = self.receive_message().decode(self.FORMAT)
        if connection_status == self.FAIL:
            print("Incorrect password...")
            self.disconnect()
            return False

        # Add join message to messages
        join_message = f"{self.username} has joined the chat !"
        self.client_info = self.make_client_info(self)
        client_info_index = self.all_client_info.index(self.client_info)
        self.messages.append(join_message)
        self.client_info = self.make_client_info(self)
        self.all_client_info[client_info_index] = self.client_info

        self.get_clients_thread.start()
        return True

    def update_all_clients(self):
        while True:
            try:
                status = self.receive_message().decode(self.FORMAT)

            except (ConnectionAbortedError, ConnectionResetError):
                break

            except AttributeError:
                self.disconnect()
                break

            client_info = self.receive_message()
            if status == "NEW CLIENT":
                client_info = pickle.loads(client_info)
                self.all_client_info.append(client_info)

            elif status == "UPDATE CLIENT INFO":
                current_client_info = pickle.loads(client_info)
                new_client_info = pickle.loads(self.receive_message())

                if new_client_info not in self.all_client_info:
                    self.all_client_info[self.all_client_info.index(current_client_info)] = new_client_info

    def make_client_info(self, client):
        username = client.username
        messages = client.messages
        port = client.PORT
        server_machine = client.server_machine
        connected = client.connected

        return ClientInfo(username, messages, port=port, server_machine=server_machine, connected=connected)

    def send_message(self, message, save_message=True):
        if self.connected:
            if (self.messages or message) and save_message:
                self.client_info = self.make_client_info(self)
                self.all_client_info.remove(self.client_info)
                self.messages.append(message)

                self.client_info = self.make_client_info(self)
                self.all_client_info.append(self.client_info)
                self.client_info = self.make_client_info(self)

                print (self.all_client_info)

            msg = message.encode(self.FORMAT)
            msg_len = len(msg)
            msg_len = str(msg_len).encode(self.FORMAT)
            msg_len += b" " * (self.HEADER - len(msg_len))

            self.client.send(msg_len)
            self.client.send(msg)

    def receive_message(self, size=HEADER):
        message = self.client.recv(size)
        if message and message is not None:
            return message

        return None

    def disconnect(self):
        self.send_message(self.DISCONNECT_MESSAGE)
        self.messages = [self.messages[-1]]
        self.client.close()
        self.connected = False

    def __repr__(self):
        return f"Client({self.username}, {self.ADDR})"


class ClientInfo:
    """Represents all the clients main info, and can be sent to the server"""
    def __init__(self, username, messages, port=5050, server_machine=socket.gethostname(), connected=True):
        self.username = username
        self.messages = messages
        self.connected = connected
        self.PORT = port
        self.server_machine = server_machine

        try:
            self.socket = socket.gethostbyname(self.server_machine)

        except socket.error:
            raise TypeError("Server machine does not exist")

        self.ADDR = (self.socket, self.PORT)

    def __repr__(self):
        return f"ClientInfo({self.username}, {self.messages})"

    def __eq__(self, other):
        return (self.username == other.username and
                self.messages == other.messages and
                self.ADDR == other.ADDR
                )


if __name__ == "__main__":
    client = Client("Aashir")
    client.connect()

    while client.connected:
        msg = input(f"{client.username}> ")
        client.send_message(msg)
        print (client.all_client_info)

