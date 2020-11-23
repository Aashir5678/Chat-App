import socket
import threading
import pickle

### MUST DISABLE FIREWALL FOR CLIENTS FROM OTHER COMPUTERS TO JOIN ###

class Server:
	"""Represents a server which clients can connect to"""
	def __init__(self, port=5050, header=1048, server_pass="", disconnect_msg="q", format_="utf-8"):
		"""
		:param port: int
		:param header: int
		:param disconnect_msg: str
		:param format: str
		"""
		self.PORT = port
		self.HEADER = header
		self.SERVER = socket.gethostbyname(socket.gethostname())
		print (self.SERVER)
		print (socket.gethostname())
		self.ADDR = (self.SERVER, self.PORT)
		self.server_password = server_pass
		self.DISCONNECT_MSG = disconnect_msg
		self.FORMAT = format_
		self.clients = {}
		self.connections = {}

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def start(self):
		"""
		Starts the server
		:returns: None
		"""
		self.server.bind(self.ADDR)
		self.server.listen(5)
		print ("server has started")

		self.to_kick = input("Kick> ")
		send_clients_thread = threading.Thread(target=self.send_clients)
		send_clients_thread.start()
		
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
		server_password = self.receive_message(conn)

		if not username:
			conn.close()
			return

		if self.server_password != server_password:
			conn.send("WRONG PASSWORD".encode(self.FORMAT))
			conn.close()
			return

		self.clients[username] = []
		self.connections[username] = conn
		connected = True

		if username == self.to_kick:
			if self.kick_client(username):
				return

		self.send_clients()

		while connected:
			try:
				message = self.receive_message(conn)

			except ConnectionResetError:
				connected = False

			except TimeoutError:
				continue

			if message == self.DISCONNECT_MSG:
				connected = False

			elif not message:
				continue

			self.clients[username].append(message)
			self.send_clients()

			print (f"{username}: {message}")
			# print (self.clients)

		print (f"{username} has disconnected")
		del self.clients[username]
		del self.connections[username]
		self.send_clients()
		conn.close()

	def receive_message(self, conn):
		"""
		Receives message from the connection provided and returns it decoded
		:returns: str
		"""
		message_len = conn.recv(self.HEADER).decode(self.FORMAT)

		if not message_len:
			return ""

		message_len = int(message_len)
		message = conn.recv(message_len).decode(self.FORMAT)

		return message

	def kick_client(self, username):
		"""
		Kicks the client with the username provided from the server
		returns True if client was successfully kicked
		:returns: bool
		"""
		conn = self.connections.get(username, False)

		if not conn:
			return conn

		conn.send("KICKED".encode(self.FORMAT))
		del self.connections[username]
		del self.clients[username]
		conn.close()
		self.send_clients()
		print (f"{username} has been kicked from the server")
		return True


	def send_clients(self):
		"""
		Sends an updated clients dictionary to every client
		:returns: None
		"""
		# clients: {"Aashir": ["hi", "what is up"]}
		# connections: {"Aashir": socket.socket}
		for conn in self.connections.values():
			for client, messages in self.clients.items():
				print ({client: messages})
				send = [client, messages]
				send = pickle.dumps(send)
				conn.send(send)

server_pass = input("Server password: ")
server = Server(server_pass=server_pass)
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