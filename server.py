import socket
import threading
import pickle

PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
HEADER = 1048
FORMAT = "utf-8"
DISCONNECT_MSG = "q"
clients = {}
connections = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def handle_client(conn, addr, connections):
	print (f"connection from {str(addr)}")
	username = receive_message(conn)
	messages = []
	clients[username] = messages
	connections.append(conn)

	if len(connections) > 1:
		send_all_clients(clients, connections)

	connected = True

	while connected:
		message = receive_message(conn)
		if message == DISCONNECT_MSG:
			connected = False

		elif not message:
			continue

		messages.append(message)

		clients[username] = messages
		send_all_clients(clients, connections)
		print (f"{username}: {message}")
		print (clients)

	print (f"{username} has disconnected !")
	conn.close()


def receive_message(conn):
	message_len = conn.recv(HEADER).decode(FORMAT)
	if not message_len:
		return

	message_len = int(message_len)

	message = conn.recv(message_len).decode(FORMAT)

	return message

def send_all_clients(clients, connections):
	for conn in connections:
		conn.send(pickle.dumps(True))
		for k, v in clients.items():
			send = [k, v]
			send = pickle.dumps(send)
			conn.send(send)

		conn.send(pickle.dumps(False))


print ("server started")
server.listen(5)
while True:
	conn, addr = server.accept()
	client_thread = threading.Thread(target=handle_client, args=(conn, addr, connections))
	client_thread.start()

server.close()