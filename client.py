import socket
import threading
import pickle


class Client:
	"""Represents a client in a server"""
	def __init__(self, username, port=5050, header=1048, format_="utf-8", server_host_name=socket.gethostname(), server_pass=""):
		"""
		:param port: int
		:param header: int
		:param format_: str
		"""
		self.PORT = port
		self.HEADER = header
		self.FORMAT = format_
		try:
			self.SERVER = socket.gethostbyname(server_host_name)

		except socket.gaierror:
			raise RuntimeError("Server host name isn't valid...")
		
		self.server_password = server_pass
		self.ADDR = (self.SERVER, self.PORT)
		self.username = username
		self.connected = False

		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = {}

	def join_server(self):
		"""
		Connects the client to the server
		:returns: bool
		"""
		try:
			self.client.connect(self.ADDR)

		except ConnectionRefusedError:
			return self.connected

		receive_clients_thread = threading.Thread(target=self.receive_clients)
		self.connected = True

		self.send_message(self.username)
		self.send_message(self.server_password)

		receive_clients_thread.start()
		return self.connected

	def send_message(self, msg):
		"""
		Sends a message to the server
		:param msg: str
		:returns: None
		"""
		if msg == "get":
			print (self.clients)
			return
                
		message = msg.encode(self.FORMAT)
		message_len = len(message)
		send_len = str(message_len).encode(self.FORMAT)
		send_len += b" " * (self.HEADER - len(send_len))

		try:
			self.client.send(send_len)
			self.client.send(message)
			return None

		except OSError:
			self.close()


	def receive_clients(self):
		"""
		Receives updated clients dictionary from server
		:returns: None
		"""
		while True:
			try:
				data = self.client.recv(self.HEADER)

			except TimeoutError:
				continue
			
			try:
				message = data.decode(self.FORMAT)

			except UnicodeDecodeError:
				pass

			else:
				if message == "KICKED":
					self.close()
					print ("Kicked from server")
					quit()
					

				elif message == "WRONG PASSWORD":
					self.close()
					print ("Wrong server password")
					quit()

			try:
				data = pickle.loads(data)

			except EOFError:
				return None

			if data:
				username, messages = data[0], data[1]
				self.clients[username] = messages

	def close(self):
		"""
		Closes the clients connection to the server
		:returns: None
		"""
		self.connected = False
		self.client.close()

username = input("Username: ")
server_pass = input("Server password: ")

client = Client(username, server_host_name='LAPTOP-USOUB7BL', server_pass=server_pass)
connected = client.join_server()
print (connected)

while connected:
	if not connected:
		break
	message = input(f"{client.username}: ")
	client.send_message(message)

	if message == "q":
		break

if not client.connected:
	client.close()