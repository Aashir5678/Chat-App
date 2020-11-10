import socket
import threading
import pickle


class Server:
	"""Represents a server which clients can connect to"""
	def __init__(self, port=5050, header=1048, disconnect_msg="q", format_="utf-8"):
		"""
		:param port: int
		:param header: int
		:param disconnect_msg: str
		:param format: str
		"""
		self.PORT = port
		self.HEADER = header
		self.SERVER = socket.gethostbyname(socket.gethostname())
		self.ADDR = (self.SERVER, self.PORT)
		self.DISCONNECT_MSG = disconnect_msg
		self.FORMAT = format_
		self.clients = {}
		self.connections = []

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def start(self):
		"""
		Starts the server
		:returns: None
		"""
		self.server.bind(self.ADDR)
		self.server.listen(5)
		print ("server has started")
		
		while True:
			conn, addr = self.server.accept()
			client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
			client_thread.start()

		self.server.close()

	def handle_client(self, conn, addr):
		"""
		Handles a client when they join
		:param addr: str
		"""
		print (f"connection from {str(addr)}")
		username = self.receive_message(conn)
		messages = []
		self.clients[username] = messages
		self.connections.append(conn)

		if len(self.connections) > 1:
			self.send_all_clients()

		connected = True

		while connected:
			message = self.receive_message(conn)
			if message == self.DISCONNECT_MSG:
				connected = False

			elif not message:
				continue

			messages.append(message)

			self.clients[username] = messages
			self.send_all_clients()
			print (f"{username}: {message}")
			print (self.clients)

		print (f"{username} has disconnected !")
		conn.close()

	def receive_message(self, conn):
		"""
		Receives a message from the connection provided and returns it
		:returns: str
		"""
		message_len = conn.recv(self.HEADER).decode(self.FORMAT)
		if not message_len:
			return

		message_len = int(message_len)

		message = conn.recv(message_len).decode(self.FORMAT)

		return message

	def send_all_clients(self):
		"""
		Sends an updated clients dictionary to every client
		:returns: None
		"""
		for conn in self.connections:
			conn.send(pickle.dumps(True))
			for k, v in self.clients.items():
				send = [k, v]
				send = pickle.dumps(send)
				conn.send(send)

			conn.send(pickle.dumps(False))

server = Server()
server.start()

# PORT = 5050
# SERVER = socket.gethostbyname(socket.gethostname())
# ADDR = (SERVER, PORT)
# HEADER = 1048
# FORMAT = "utf-8"
# DISCONNECT_MSG = "q"
# clients = {}
# connections = []
# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(ADDR)

# def handle_client(conn, addr, connections):
# 	print (f"connection from {str(addr)}")
# 	username = receive_message(conn)
# 	messages = []
# 	clients[username] = messages
# 	connections.append(conn)

# 	if len(connections) > 1:
# 		send_all_clients(clients, connections)

# 	connected = True

# 	while connected:
# 		message = receive_message(conn)
# 		if message == DISCONNECT_MSG:
# 			connected = False

# 		elif not message:
# 			continue

# 		messages.append(message)

# 		clients[username] = messages
# 		send_all_clients(clients, connections)
# 		print (f"{username}: {message}")
# 		print (clients)

# 	print (f"{username} has disconnected !")
# 	conn.close()


# def receive_message(conn):
# 	message_len = conn.recv(HEADER).decode(FORMAT)
# 	if not message_len:
# 		return

# 	message_len = int(message_len)

# 	message = conn.recv(message_len).decode(FORMAT)

# 	return message




# print ("server started")
# server.listen(5)
# while True:
# 	conn, addr = server.accept()
# 	client_thread = threading.Thread(target=handle_client, args=(conn, addr, connections))
# 	client_thread.start()

# server.close()