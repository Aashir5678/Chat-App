import socket
import threading
import pickle

PORT = 5050
HEADER = 1048
FORMAT = "utf-8"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clients = {}

client.connect(ADDR)

def send_message(msg):
	message = msg.encode(FORMAT)
	message_len = len(message)
	send_len = str(message_len).encode(FORMAT)
	send_len += b" " * (HEADER - len(send_len))

	client.send(send_len)
	client.send(message)

def receive_clients():
	while True:
		update_clients = client.recv(HEADER)
		update_clients = pickle.loads(update_clients)

		if update_clients:
			if not isinstance(update_clients, bool):
				k, v = update_clients[0], update_clients[1]
				clients[k] = v
				print (clients)


name = input("username: ")
send_message(name)

receive_clients_thread = threading.Thread(target=receive_clients)
receive_clients_thread.start()

while True:
	message = input("To quit press q > ")
	send_message(message)

	if message == "q":
		break

client.close()