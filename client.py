# Author: Aashir

import socket
import threading
import pickle
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
		self.clients = {}
		self.messages = []

	def join_server(self):
		"""
		Connects the client to the server
		:returns: bool
		"""

		self.client.settimeout(20)

		try:
			self.client.connect(self.ADDR)

		except ConnectionRefusedError as e:
			return self.connected

		except WindowsError as e:
			if e.winerror == 10060:
				print ("couldn't connect to server because it took too long to respond or it has failed to respond")

			return self.connected

		except socket.timeout:
			print ("timed out :/")
			return self.connected

		else:
			self.client.settimeout(None)

		# Start receiving any new clients or new client messages
		receive_clients_thread = threading.Thread(target=self.receive_clients)
		receive_clients_thread.start()

		self.connected = True
		self.send_message(self.username)
		self.send_message(self.server_password)

		return self.connected

	def send_message(self, msg):
		"""
		Sends a message to the server
		:param msg: str
		:returns: None
		"""
		if msg == "get":
			print (self.messages)
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
		Receives updated clients dictionary from server
		:returns: None
		"""
		while True:
			try:
				data = self.client.recv(self.HEADER)

			except TimeoutError:
				continue

			except (ConnectionAbortedError, ConnectionResetError):
				break
			
			try:
				message = data.decode(self.FORMAT)

			except UnicodeDecodeError:
				pass

			# If data is a string
			else:
				if message == self.DISCONNECT_MSG:
					print ("Kicked from server")
					break

				elif message == "WRONG PASSWORD":
					print ("Wrong server password")
					break

				else:
					self.messages.append(message)

			# If data is not a string
			try:
				data = pickle.loads(data)

			except EOFError:
				return None

			except UnpicklingError:
				pass

			# If data is a list
			if data:
				try:
					username, messages = data[0], data[1]
					self.clients[username] = messages

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
	server_pass = input("Server password: ")
	server_ip = "192.168.157.1"

	client = Client(username, server_ip, server_pass=server_pass)
	client.join_server()

	while client.connected:
		message = input(f"{client.username}: ")
		client.send_message(message)

		if message == "q":
			break

	print ("not connected")
	if client.connected:
		client.close()

