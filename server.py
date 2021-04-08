"""
Author: Aashir Alam

MUST DISABLE FIREWALL ON THIS COMPUTER FOR OTHER COMPUTERS TO JOIN

"""

import socket
import threading
import pickle

class Server:
	"""Represents a server which clients can connect to and send messages to"""
	def __init__(self, port=5050, header=1048, server_pass="", format_="utf-8"):
		"""
		:param port: int
 		:param header: int
		:param format: str
		"""
		self.PORT = port
		self.HEADER = header
		self.SERVER = socket.gethostbyname(socket.gethostname())
		print (self.SERVER)
		print (socket.gethostname())
		self.ADDR = (self.SERVER, self.PORT)
		self.server_password = server_pass
		self.FORMAT = format_
		self.started = False
		self.lock = threading.Lock()

		# "aashir": [conn, [messages]]
		self.clients = {}
		# ordered messages
		self.messages = []

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def bind_server(self):
		"""
		Attempts to bind the server to self.ADDR, returns true if binding wsa successful
		:returns: bool
		"""
		try:
			self.server.bind(self.ADDR)
			return True

		except:
			return False

	def start(self):
		"""
		Starts the server
		:returns: None
		"""
		self.started = True

		try:
			self.server.listen(5)

		except:
			return None

		print ("server has started")
		# print (self.port_in_use(self.PORT))

		# Wait for any incoming connections, and handle that connection
		while True:
			try:
				conn, addr = self.server.accept()

			except OSError:
				break

			client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
			client_thread.setDaemon(True)
			client_thread.start()

		self.close()

	def handle_client(self, conn, addr):
		"""
		Handles a client when they join
		:param conn: socket.socket
		:param addr: str
		"""
		print (f"connection from {str(addr)}")
		username = self.receive_message(conn)
		server_password = self.receive_message(conn)

		if not username or username in self.clients:
			conn.close()
			return

		if self.server_password != server_password:
			conn.send("WRONG PASSWORD".encode(self.FORMAT))
			conn.close()
			return

		# Store client and send all messges to client
		connected = True
		join_message = f"{username} has joined the chat."

		self.lock.acquire()
		self.messages.append(join_message)
		self.lock.release()
		self.send_clients(new_message=join_message)
		self.clients[username] = [conn, []]

		for message in self.messages:
			print (f"Sending message to new client {username}: {message}")
			self.send_clients(username=username, new_message=message)

		while connected:
			try:
				message = self.receive_message(conn)

			except ConnectionResetError:
				connected = False
				break

			except TimeoutError:
				continue

			if not message:
				connected = False
				break

			# Add message to clients dictionary, and send that message to every other client

			self.lock.acquire()
			self.clients[username][1].append(message)
			message = f"{username}: {message}"
			print (message)

			self.messages.append(message)
			self.send_clients(new_message=message)
			self.lock.release()

		self.disconnect_client(conn, username)

	def receive_message(self, conn):
		"""
		Receives message from the connection provided and returns it decoded
		:returns: str
		"""
		try:
			message_len = conn.recv(self.HEADER).decode(self.FORMAT)

		except ConnectionAbortedError:
			return ""

		except OSError:
			return ""

		if not message_len:
			return ""

		message_len = int(message_len)
		message = conn.recv(message_len).decode(self.FORMAT)

		return message

	def send_clients(self, username="", new_message=None):
		"""
		Sends an updated clients dictionary to every client, 
		sends new message to every client or just the client
		with the username specified. Returns True if send was
		successful.

		:param username: str
		:param new_message: str
		:returns: bool
		"""

		# clients: {"Aashir": [conn, ["hi", "whats up", "messages"]]}
		# print (self.clients)
		for client_username, client_info in self.clients.items():
			conn, messages = client_info
			send = [client_username, messages]
			send = pickle.dumps(send)
			try:
				conn.send(send)

			except ConnectionResetError:
				print (self.clients)
				self.disconnect_client(conn, client_username)
				break

			

		if new_message is not None:
			if not username:
				for client_info in self.clients.values():
					conn = client_info[0]
					conn.send(new_message.encode(self.FORMAT))

			else:
				if username is None:
					return False

				client_info = self.clients.get(username, None)
				if client_info is not None:
					conn = client_info[0]

				conn.send(new_message.encode(self.FORMAT))

		return True

	def disconnect_client(self, conn, username):
		"""
		Disconnects the client with the username provided, returns true if client was successfully disconnected
		:param conn: socket.socket
		:param username: str
		:returns: bool
		"""
		if username not in self.clients:
			return False

		self.lock.acquire()
		self.clients[username][1].append(False)

		conn.close()
		disconnect_msg = f"{username} has disconnected."
		self.messages.append(disconnect_msg)
		self.send_clients(new_message=disconnect_msg)
		return True

	def close(self):
		print ("server closed")
		self.server.close()





if __name__ == "__main__":
	server = Server()
	server.bind_server()
	server.start()



# class Server:
# 	"""Represents a server which clients can connect to and send messages to"""
# 	def __init__(self, port=5050, header=1048, server_pass="", format_="utf-8"):
# 		"""
# 		:param port: int
# 		:param header: int
# 		:param format: str
# 		"""
# 		self.PORT = port
# 		self.HEADER = header
# 		self.SERVER = socket.gethostbyname(socket.gethostname())
# 		print (self.SERVER)
# 		print (socket.gethostname())
# 		self.ADDR = (self.SERVER, self.PORT)
# 		self.server_password = server_pass
# 		self.FORMAT = format_
# 		self.started = False

# 		self.lock = threading.Lock()
# 		self.clients = {}
# 		self.connections = {}
# 		self.messages = []

# 		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 	def bind_server(self):
# 		"""
# 		Attempts to bind the server to self.ADDR, returns true if binding wsa successful
# 		:returns: bool
# 		"""
# 		try:
# 			self.server.bind(self.ADDR)
# 			return True

# 		except:
# 			return False

# 	def start(self):
# 		"""
# 		Starts the server
# 		:returns: None
# 		"""
# 		self.started = True

# 		try:
# 			self.server.listen(5)

# 		except:
# 			return None

# 		print ("server has started")
# 		# print (self.port_in_use(self.PORT))

# 		# Wait for any incoming connections, and handle that connection
# 		while True:
# 			try:
# 				conn, addr = self.server.accept()

# 			except OSError:
# 				break

# 			client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
# 			client_thread.setDaemon(True)
# 			client_thread.start()

# 		self.close()

# 	def handle_client(self, conn, addr):
# 		"""
# 		Handles a client when they join
# 		:param conn: socket.socket
# 		:param addr: str
# 		"""
# 		print (f"connection from {str(addr)}")
# 		username = self.receive_message(conn)
# 		server_password = self.receive_message(conn)

# 		if not username or username in self.connections:
# 			conn.close()
# 			return

# 		if self.server_password != server_password:
# 			conn.send("WRONG PASSWORD".encode(self.FORMAT))
# 			conn.close()
# 			return

# 		# Store client and send all messges to client
# 		connected = True
# 		join_message = f"{username} has joined the chat."

# 		self.lock.acquire()

# 		self.clients[username] = []
# 		# self.clients[username].append(join_message)
# 		self.connections[username] = conn
# 		self.messages.append(join_message)

# 		self.lock.release()

# 		self.send_clients(new_message=join_message)

# 		for message in self.messages:
# 			self.send_clients(username=username, new_message=message)

# 		while connected:
# 			try:
# 				message = self.receive_message(conn)

# 			except ConnectionResetError:
# 				connected = False
# 				break

# 			except TimeoutError:
# 				continue

# 			if not message:
# 				connected = False
# 				break

# 			# Add message to clients dictionary, and send that message to every other client

# 			self.lock.acquire()
# 			self.clients[username].append(message)
# 			message = f"{username}: {message}"
# 			print (message)

# 			self.messages.append(message)
# 			self.send_clients(new_message=message)
# 			self.lock.release()

# 		self.disconnect_client(conn, username)

# 	def receive_message(self, conn):
# 		"""
# 		Receives message from the connection provided and returns it decoded
# 		:returns: str
# 		"""
# 		try:
# 			message_len = conn.recv(self.HEADER).decode(self.FORMAT)

# 		except ConnectionAbortedError:
# 			return ""

# 		except OSError:
# 			return ""

# 		if not message_len:
# 			return ""

# 		message_len = int(message_len)
# 		message = conn.recv(message_len).decode(self.FORMAT)

# 		return message

# 	def kick_client(self, username):
# 		"""
# 		Kicks the client with the username provided from the server
# 		returns True if client was successfully kicked
# 		:returns: bool
# 		"""
# 		conn = self.connections.get(username, False)

# 		if not conn:
# 			return conn

# 		# Notify that client has been kicked and delete client connections and clients dictionaries
		
# 		conn.send("KICKED".encode(self.FORMAT))
# 		self.lock.acquire()
# 		del self.connections[username]
# 		del self.clients[username]
# 		self.lock.release()

# 		disconnect_msg = f"{username} has been kicked."
# 		conn.close()
# 		self.messages.append(disconnect_msg)
# 		print (disconnect_msg)
# 		self.send_clients(new_message=disconnect_msg)
# 		return True


# 	def send_clients(self, username="", new_message=None):
# 		"""
# 		Sends an updated clients dictionary to every client, 
# 		sends new message to every client or just the client
# 		with the username specified. Returns True send was
# 		successful.

# 		:param username: str
# 		:param new_message: str
# 		:returns: bool
# 		"""
# 		# clients: {"Aashir": ["hi", "what is up"]}
# 		# connections: {"Aashir": socket.socket}
# 		disconnect = False
# 		for conn in self.connections.values():
# 			for client_username, messages in self.clients.items():
# 				send = [client_username, messages]
# 				send = pickle.dumps(send)
# 				try:
# 					conn.send(send)

# 				except ConnectionResetError:
# 					print (self.clients)
# 					print (self.connections)
# 					disconnect = True
# 					break


# 			if disconnect:
# 				self.disconnect_client(conn, client_username)
# 				break

# 		if new_message is not None:
# 			if not username:
# 				for conn in self.connections.values():
# 					conn.send(new_message.encode(self.FORMAT))

# 			else:
# 				conn = self.connections.get(username, None)

# 				if username is None:
# 					return False

# 				conn.send(new_message.encode(self.FORMAT))

# 		return True

# 	def disconnect_client(self, conn, username):
# 		"""
# 		Disconnects the client with the username provided, returns true if client was successfully disconnected
# 		:param conn: socket.socket
# 		:param username: str
# 		:returns: bool
# 		"""
# 		if username not in self.clients or username not in self.connections:
# 			return False

# 		self.lock.acquire()
# 		self.clients[username].append(False)
# 		del self.connections[username]
# 		self.lock.release()

# 		conn.close()
# 		disconnect_msg = f"{username} has disconnected."
# 		self.messages.append(disconnect_msg)
# 		self.send_clients(new_message=disconnect_msg)
# 		return True

# 	def close(self):
# 		print ("server closed")
# 		self.server.close()


# if __name__ == "__main__":
# 	server_pass = input("Server password: ")
# 	server = Server(server_pass=server_pass)
# 	server.bind_server()
# 	server.start()

