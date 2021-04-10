
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
		self.DISCONNECT_MSG = "!DISCONNECT".encode("utf-8")
		self.HEADER = header
		self.SERVER = socket.gethostbyname(socket.gethostname())
		self.ADDR = (self.SERVER, self.PORT)
		print (self.ADDR)
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
				print (conn, addr)

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
				print ("conn reset")
				connected = False
				break

			except TimeoutError:
				continue

			if isinstance(message, Exception):
				print ("error msg")
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

		print ("broke loop")
		self.disconnect_client(username)

	def receive_message(self, conn):
		"""
		Receives message from the connection provided and returns it decoded
		:param conn: socket.socket
		:returns: str / Exception
		"""
		try:
			message_len = conn.recv(self.HEADER).decode(self.FORMAT)

		except (ConnectionAbortedError, OSError) as e:
			return e

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
				self.disconnect_client(client_username)
				break

			# If client is kicked
			except OSError:
				pass

		if new_message is not None:
			if not username:
				for client_info in self.clients.values():
					conn = client_info[0]
					try:
						conn.send(new_message.encode(self.FORMAT))

					except OSError:
						pass

			else:
				if username is None:
					return False

				client_info = self.clients.get(username, None)
				if client_info is not None:
					conn = client_info[0]

				try:
					conn.send(new_message.encode(self.FORMAT))

				except OSError:
					pass

		return True

	def kick_client(self, username):
		"""
		Kicks the client with the username provided, returns true if client was successfully kicked
		:param username: str
		:returns: bool
		"""
		print (f"kicking client: {username}")
		if username not in self.clients:
			print ("non existing client")
			return False

		self.lock.acquire()
		self.clients[username][1].append(False)
		conn = self.clients[username][0]
		conn.send(self.DISCONNECT_MSG)

		conn.close()
		disconnect_msg = f"{username} has been kicked."
		print (disconnect_msg)
		self.messages.append(disconnect_msg)
		self.send_clients(new_message=disconnect_msg)
		self.lock.release()

		return True

	def disconnect_client(self, username):
		"""
		Disconnects the client with the username provided, returns true if client was successfully disconnected
		:param username: str
		:returns: bool
		"""
		if username not in self.clients:
			return False

		elif False in self.clients[username][1]:
			return False

		self.lock.acquire()
		self.clients[username][1].append(False)
		conn = self.clients[username][0]
		try:
			conn.send(self.DISCONNECT_MSG)

		except OSError:
			pass

		conn.close()
		disconnect_msg = f"{username} has disconnected."
		print (disconnect_msg)
		self.messages.append(disconnect_msg)
		self.send_clients(new_message=disconnect_msg)
		self.lock.release()

		return True

	def close(self):
		print ("server closed")
		self.server.close()



if __name__ == "__main__":
	server = Server()
	bound = server.bind_server()
	print (bound)
	server.start()


