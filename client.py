import socket
import pickle


class Client:
    def __init__(self, username, port=5050):
        self.PORT = port
        self.HEADER = 64
        self.username = username
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.socket = socket.gethostbyname(socket.gethostname())

        self.connected = True
        self.messages = []
        self.client_usernames = []
        self.clients = []

        self.ADDR = (self.socket, self.PORT)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.client.connect(self.ADDR)
        self.send_message(self.username)
        self.receive_usernames()

    def send_message(self, message):
        msg = message.encode(self.FORMAT)
        msg_len = len(msg)
        msg_len = str(msg_len).encode(self.FORMAT)
        msg_len += b" " * (self.HEADER - len(msg_len))

        self.client.send(msg_len)
        self.client.send(msg)

    def receive_usernames(self):
        usernames = self.client.recv(self.HEADER)
        usernames = pickle.loads(usernames)

        self.client_usernames = usernames

    def disconnect(self):
        self.messages.clear()
        self.client.close()
        self.connected = False

    def __repr__(self):
        return f"Client({self.username}, {self.ADDR})"


if __name__ == "__main__":
    client = Client("Aashir")
    client.connect()
    while True:
        msg = input(f"{client.username}> ")
        client.send_message(msg)


#
# class Client:
#     def __init__(self, username, port=5050):
#         self.PORT = port
#         self.HEADER = 1048
#         self.username = username
#         self.FORMAT = "utf-8"
#         self.DISCONNECT_MESSAGE = "!DISCONNECT"
#         self.socket = socket.gethostbyname(socket.gethostname())
#         self.connected = True
#         self.messages = []
#
#         self.ADDR = (self.socket, self.PORT)
#
#         self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.client.connect(self.ADDR)
#         self.send_message(self.username)
#
#     def send_message(self, msg):
#         """Sends a message to the server"""
#         if msg != self.username:
#             self.messages.append(msg)
#
#         if msg == self.DISCONNECT_MESSAGE:
#             self.connected = False
#         message = msg.encode(self.FORMAT)
#         # message_len = len(message)
#         # send_len = str(message_len).encode(self.FORMAT)
#         # send_len += b' ' * (self.HEADER - len(send_len))
#         #
#         # self.client.send(send_len)
#         self.client.send(message)
#
#         if not self.connected:
#             quit()
#
#         print (self.messages)
#
#     def receive_msg(self):
#         """Receives a message from the server"""
#         message = self.client.recv(self.HEADER).decode(self.FORMAT)
#
#         if message:
#             print (message)
#
#         else:
#             return
#
#     def __repr__(self):
#         return f"({self.username}, {self.ADDR})"
#
#
# if __name__ == "__main__":
#     username = input("Username: ")
#     client = Client(username)
#
#     while True:
#         msg = input(f"{username}> ")
#         client.send_message(msg)
#
