# Author: Aashir

import socket
import threading
import pickle
from time import time
from _pickle import UnpicklingError

class Client:
	"""Represents a client which can join and send messages to a Server"""
	def __init__(self, username, server_ip, port=5050, header=1048, format_="utf-8", server_pass=""):
		"""
		:param port: int
		:param header: int
		:param format_: str
		"""
		self.PORT = port
		self.HEADER = header
		self.FORMAT = format_
		self.SERVER = server_ip
		self.DISCONNECT_MSG = "!DISCONNECT"

		self.server_password = server_pass
		self.ADDR = (self.SERVER, self.PORT)
		self.username = username
		self.connected = False

		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = []
		self.messages = []

	def __str__(self):
		return f"{self.username} ({self.SERVER}, {self.PORT})"

	def join_server(self):
		"""
		Connects the client to the server
		:returns: bool
		"""

		self.client.settimeout(20)

		try:
			self.client.connect(self.ADDR)

		except ConnectionRefusedError as e:
			return False

		except socket.timeout:
			print ("timed out")
			return False

		except WindowsError as e:
			if e.winerror == 10060:
				print ("couldn't connect to server because it took too long to respond or it has failed to respond")

			return False

		else:
			self.client.settimeout(None)

		# Start receiving any new clients or new client messages
		receive_clients_thread = threading.Thread(target=self.receive_clients)
		receive_clients_thread.start()

		self.connected = True
		self.send_message(self.username)
		self.send_message(self.server_password)
		self.clients.append(self.username)

		return True

	def send_message(self, msg):
		"""
		Sends a message to the server
		:param msg: str
		:returns: None
		"""
		if msg == "get":
			print (self.messages)
			print (self.clients)
			return None
        
        # Find out message length, and send to client before sending message

		message = msg.encode(self.FORMAT)
		message_len = len(message)
		send_len = str(message_len).encode(self.FORMAT)
		send_len += b" " * (self.HEADER - len(send_len))

		try:
			self.client.send(send_len)
			self.client.send(message)

		except OSError:
			self.close()


	def receive_clients(self):
		"""
		Receives updated clients dictionary
		or any new messages from server
		:returns: None
		"""
		
		while True:
			try:
				data = self.client.recv(self.HEADER)

			except TimeoutError:
				continue

			except (ConnectionAbortedError, ConnectionResetError):
				break

			if data.isascii():
				message = data.decode(self.FORMAT)

				if message == self.DISCONNECT_MSG:
					print ("Disconnected from server")
					break

				elif message == "WRONG PASSWORD":
					print ("Wrong server password")
					break

				else:
					username = message.split(" ")[0]
					if "has been kicked" in message or "has been disconnected" in message:
						self.clients.remove(username)
					
					self.messages.append(message)

			else:
				try:
					data = pickle.loads(data)

				except (EOFError, UnpicklingError):
					break

				# Receive new client and add to clients list
				try:
					username = data[0]
					if username not in self.clients:
						self.clients.append(username)

				except TypeError:
					print ("Invalid data: " + str(data))

		print ("closed")
		self.close()
		quit()


	def close(self):
		"""
		Closes the clients connection to the server
		:returns: None
		"""
		self.connected = False
		self.client.close()


if __name__ == "__main__":
	username = input("Username: ")
    host_name = input("Host Name (leave blank for localhost): ")
    server_pass = input("Server password: ")

	if host_name:
		server_ips = socket.gethostbyname_ex(host_name)[-1]

	else:
		server_ips = socket.gethostbyname_ex(socket.gethostname())[-1]

	for server_ip in server_ips:
		client = Client(username, server_ip, server_pass=server_pass)
		connected = client.join_server()

		if connected:
			break

	while client.connected:
		message = input(f"{client.username}: ")
		client.send_message(message)

		if message == "q":
			break

	print ("not connected")
	if client.connected:
		client.close()
