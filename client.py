import socket
import threading
import pickle


class Client:
	"""Represents a client in a server"""
	def __init__(self, username, port=5050, header=1048, format_="utf-8", server_host=socket.gethostname()):
		"""
		:param port: int
		:param header: int
		:param format_: str
		"""
		self.PORT = port
		self.HEADER = header
		self.FORMAT = format_
		try:
			self.SERVER = socket.gethostbyname(server_host)

		except socket.gaierror:
			raise RuntimeError("Server host isn't valid...")
			
		self.ADDR = (self.SERVER, self.PORT)
		self.username = username

		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = {}

	def join_server(self):
		"""
		Connects the client to the server
		:returns: None
		"""
		self.client.connect(self.ADDR)
		self.send_message(self.username)

		receive_clients_thread = threading.Thread(target=self.receive_clients)
		receive_clients_thread.start()

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

		self.client.send(send_len)
		self.client.send(message)

	def receive_clients(self):
		"""
		Receives updated clients dictionary from server
		:returns: None
		"""
		while True:
			update_clients = self.client.recv(self.HEADER)
			update_clients = pickle.loads(update_clients)

			if update_clients:
				if not isinstance(update_clients, bool):
					k, v = update_clients[0], update_clients[1]
					self.clients[k] = v

	def close(self):
		"""
		Closes the clients connection to the server
		:returns: None
		"""
		self.client.close()


client = Client(input("Username: "), server_host='LAPTOP-USOUB7BL')
client.join_server()

while True:
	message = input("> ")
	client.send_message(message)

	if message == "q":
		break
