import socket
import threading
import pickle
from client import Client


class Server:
    HEADER = 64

    def __init__(self, port=5050):
        self.PORT = port
        self.HEADER = 64
        self.FORMAT = "utf-8"
        self.DISCONNECT_MESSAGE = "!DISCONNECT"
        self.SERVER = socket.gethostbyname(socket.gethostname())

        self.connected_clients = []
        self.ADDR = (self.SERVER, self.PORT)
        self.closed = False

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server.bind(self.ADDR)
        self.server.listen(5)

        print ("server has started...")
        while not self.closed:
            conn, addr = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()

    def handle_client(self, conn, addr):
        client = self.create_client(conn)

        self.connected_clients.append(client)
        print (client.username + " has joined the chat !")

        while client.connected:
            message_len = self.receive_message(conn)
            if message_len:
                message_len = int(message_len)
                message = self.receive_message(conn, size=message_len)
                if message == self.DISCONNECT_MESSAGE:
                    client.connected = False
                    break

                elif message is None:
                    continue

                print (client.username + "> " + message)

        print(f"{client.username} has disconnected !")
        self.connected_clients.remove(client)
        client.disconnect()

    def create_client(self, conn):
        message_len = self.receive_message(conn)
        if message_len:
            message_len = int(message_len)
            message = self.receive_message(conn, size=message_len)

        else:
            return None

        client = Client(message)
        self.connected_clients.append(client)

        usernames = [client.username for client in self.connected_clients]
        usernames = pickle.dumps(usernames)

        conn.send(usernames)

        return client

    def receive_message(self, conn, size=HEADER):
        message = conn.recv(size).decode(self.FORMAT)
        if message:
            return message

        return None

    def close(self):
        self.server.close()

    def __repr__(self):
        return f"SERVER {self.PORT}"


if __name__ == "__main__":
    server = Server()
    server.start()

#
# class Server:
#     def __init__(self, port=5050):
#         self.PORT = port
#         self.HEADER = 1048
#         self.FORMAT = "utf-8"
#         self.DISCONNECT_MESSAGE = "!DISCONNECT"
#         self.SERVER = socket.gethostbyname(socket.gethostname())
#         self.clients = []
#         self.ADDR = (self.SERVER, self.PORT)
#         self.closed = False
#
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.bind(self.ADDR)
#
#         print ("[START] server is starting...")
#         self.start()
#
#     def start(self):
#         """Starts the server"""
#         self.server.listen()
#
#         while True:
#             conn, addr = self.server.accept()
#
#             thread = threading.Thread(target=self.handle_client, args=(conn,))
#             thread.start()
#
#             print (f"[CLIENTS] number of clients {threading.activeCount() - 1}")
#
#     def handle_client(self, conn):
#         """Handles a client when they join"""
#
#         username = self.receive_msg(conn=conn)
#         client = Client(username)
#         self.clients.append(client)
#         print(f"[NEW CLIENT] new client {client.username}")
#         msg = True
#
#         while msg:
#             msg = self.receive_msg()
#             if msg is False or self.closed:
#                 break
#
#             msg = f"{client.username}> {msg}"
#
#             print (client.messages)
#
#         print (f"[DISCONNECT] {client.username} disconnected")
#         conn.close()
#
#     def receive_msg(self, conn=None):
#         """Receives messages from the client connection"""
#         if self.clients:
#             client = self.clients[-1].client
#
#         elif conn is not None:
#             client = conn
#
#         else:
#             return
#
#         message = client.recv(self.HEADER).decode(self.FORMAT)
#         if message:
#             if self.clients:
#                 self.clients[-1].messages.append(message)
#
#             if message == self.DISCONNECT_MESSAGE:
#                 client_connected = False
#                 return client_connected
#
#             return message
#
#     def close(self):
#         """Closes the server"""
#         self.closed = True
#         self.server.shutdown(socket.SHUT_RDWR)
#         self.server.close()
#
#
# if __name__ == "__main__":
#     server = Server()
