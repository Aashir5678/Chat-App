# Author: Aashir

import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter.messagebox import showerror
from tkinter.messagebox import showinfo
from threading import Thread
from server import Server
from string import ascii_letters
from _tkinter import TclError


class ServerGUI:
	def __init__(self, parent):
		self.parent = parent
		self.server = None
		self.server_thread = Thread(target=self.start_server)
		self.parent.title("Server")
		self.parent.geometry("300x200")
		self.parent.resizable(False, False)

		self.PortLabel = tk.Label(self.parent, text="Port:")
		self.PortEntry = tk.Entry(self.parent)
		self.PortEntry.insert(0, "5050")

		self.ServerPasswordLabel = tk.Label(self.parent, text="Server Password:")
		self.ServerPasswordEntry = tk.Entry(self.parent, show="*")

		self.StartServerButton = tk.Button(self.parent, text="Start Server", width=25, height=2)
		self.StartServerButton.bind("<Button-1>", lambda event: self.server_thread.start())

		# When the "x" in the top right is clicked, call self.quit
		self.parent.protocol("WM_DELETE_WINDOW", self.quit)

		self.PortLabel.pack()
		self.PortEntry.pack(pady=10, ipady=5)

		self.ServerPasswordLabel.pack()
		self.ServerPasswordEntry.pack(pady=10, ipady=5)

		self.StartServerButton.pack()

	@staticmethod
	def color_code_listbox(listbox):
		for index, message in enumerate(listbox.get(0, tk.END)):
			# Change disconnect messages to red
			if ":" not in message and "disconnected" in message:
				listbox.itemconfig(index, {"fg": "red"})

			# Change join messages to green
			elif ":" not in message and "joined" in message:
				listbox.itemconfig(index, {"fg": "green"})

			# Change kick messages to orange
			elif ":" not in message and "kicked" in message:
				listbox.itemconfig(index, {"fg": "orange"})

	def start_server(self):
		server_port = self.PortEntry.get()
		server_password = self.ServerPasswordEntry.get()

		if not server_port:
			showerror("Invalid port", "Invalid port")
			self.server_thread = Thread(target=self.start_server)
			return None

		try:
			server_port = int(server_port)

		except ValueError:
			showerror("Invalid port", "Invalid port")
			self.server_thread = Thread(target=self.start_server)
			return None

		if server_password:
			for char in server_password:
				if char in ascii_letters:
					break

			else:
				showerror("Invalid password", "Invalid characters in password")
				self.server_thread = Thread(target=self.start_server)
				return None

		self.server = Server(port=server_port, server_pass=server_password)
		port_open = self.server.bind_server()

		if not port_open:
			showerror("Invalid port", "Port is already in use, try using a different port.")
			self.server_thread = Thread(target=self.start_server)
			return None

		for widget in self.parent.winfo_children():
			widget.destroy()

		self.parent.geometry("350x350")

		self.PortLabel = tk.Label(self.parent, text=f"Port: {str(server_port)}")
		self.HostLabel = tk.Label(self.parent, text=f"Host Name: {self.server.HOST}")
		
		if server_password:
			self.PasswordLabel = tk.Label(self.parent, text=f"Server password: {server_password}")

		self.ClientsLabel = tk.Label(self.parent, text="Clients:")
		self.ClientsListbox = tk.Listbox(self.parent, height=15, width=50)
		self.ClientsScrollbar = tk.Scrollbar(self.parent)
		self.ClientsScrollbar.bind("<Button-1>", lambda event: self.display_client())

		self.KickClientButton = tk.Button(self.parent, text="Kick Client", command=self.kick_client)
		self.ViewMessagesButton = tk.Button(self.parent, text="View Messages", command=self.view_messages)
		self.BannedIPButton = tk.Button(self.parent, text="Banned IP's", command=self.display_banned_ips)

		# Scrollbar binding

		self.ClientsListbox.config(yscrollcommand=self.ClientsScrollbar.set)
		self.ClientsScrollbar.config(command=self.ClientsListbox.yview)

		self.PortLabel.pack()

		if server_password:
			self.PasswordLabel.pack()

		self.HostLabel.pack(pady=5)

		self.KickClientButton.pack(side=tk.BOTTOM)
		self.ViewMessagesButton.pack(side=tk.BOTTOM)
		self.BannedIPButton.pack(side=tk.BOTTOM)

		self.ClientsLabel.pack()
		self.ClientsScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.ClientsListbox.pack(expand=True)

		self.update_clients_listbox()

		showinfo("Notice", "Must disable firewall on this computer\nfor clients from other computers to join.")
		self.server.start()


	def update_clients_listbox(self):
		self.ClientsListbox.delete(0, tk.END)

		# Insert all client messages except if client has disconnected
		for client_username, client_info in self.server.clients.items():
			if False not in client_info[1]:
				self.ClientsListbox.insert(tk.END, f"{client_username} ({client_info[-1][0]})")

		self.parent.after(10, self.update_clients_listbox)

	def kick_client(self):
		client_username = askstring("Kick Client", "Which client do you wisht to kick ?")

		if client_username and client_username is not None and client_username in self.server.clients:
			kicked = self.server.kick_client(client_username)

	def display_banned_ips(self):
		self.BannedIPs = tk.Toplevel(self.parent)
		self.BannedIPs.geometry("400x400")
		self.BannedIPs.title("Banned Clients")
		self.BannedIPs.resizable(False, False)

		self.BannedIPsLabel = tk.Label(self.BannedIPs, text="Banned IP's:")
		self.BannedIPsListbox = tk.Listbox(self.BannedIPs, width=50, height=15)
		for ip in self.server.banned_ips:
			self.BannedIPsListbox.insert(tk.END, ip)

		self.BanIPLabel = tk.Label(self.BannedIPs, text="Ban IP:")
		self.BanIPEntry = tk.Entry(self.BannedIPs)
		self.BanIPEntry.bind("<Return>", lambda event: self.ban_ip())

		self.UnBanIPButton = tk.Button (self.BannedIPs, 
			text="Unban IP", 
			command=self.unban_ip
			)

		self.BanIPLabel.pack()
		self.BanIPEntry.pack(pady=10)
		self.UnBanIPButton.pack(pady=10)
		self.BannedIPsListbox.pack(side=tk.BOTTOM, pady=10)
		self.BannedIPsLabel.pack(side=tk.BOTTOM)
		self.update_banned_ips_listbox()


	def update_banned_ips_listbox(self):
		try:
			self.BannedIPsListbox.delete(0, tk.END)

		except TclError:
			return

		for ip in self.server.banned_ips:
			self.BannedIPsListbox.insert(tk.END, ip)

		self.parent.after(10, self.update_banned_ips_listbox)


	def ban_ip(self):
		ip = self.BanIPEntry.get()
		banned = self.server.ban_ip(ip)

		if not banned:
			showerror("Invalid IP", "IP address provided is invalid.")

		self.BanIPEntry.delete(0, tk.END)

	def unban_ip(self):
		ip = askstring("Unban IP", "Which IP do you want to unban ?", parent=self.BannedIPs)
		self.server.unban_ip(ip)

	def view_messages(self):
		self.ClientMessages = tk.Toplevel(self.parent)
		self.ClientMessages.geometry("500x300")
		self.ClientMessages.title("Messages")
		self.ClientMessages.resizable(False, False)

		self.MessagesScrollbar = tk.Scrollbar(self.ClientMessages)
		self.MessagesListbox = tk.Listbox(self.ClientMessages, width=50, height=18)

		self.MessagesListbox.config(yscrollcommand=self.MessagesScrollbar.set)
		self.MessagesScrollbar.config(command=self.MessagesListbox.yview)

		self.update_messages_listbox()

		self.MessagesScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.MessagesListbox.pack(expand=True)

	def update_messages_listbox(self):
		try:
			self.MessagesListbox.delete(0, tk.END)
			for message in self.server.messages:
				self.MessagesListbox.insert(tk.END, message)

			self.color_code_listbox(self.MessagesListbox)

			self.parent.after(10, self.update_messages_listbox)
		
		# When trying to close window
		except TclError:
			return

	def quit(self):
		if self.server is not None:
			self.server.close()

		self.parent.destroy()
		quit()


if __name__ == "__main__":
	parent = tk.Tk()
	ServerGUI(parent)
	parent.mainloop()
	