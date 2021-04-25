# Author: Aashir

import tkinter as tk
from tkinter import TclError
from client import Client
from ServerGUI import ServerGUI
from time import sleep
from socket import gethostbyname_ex, gethostbyname, gethostname, gaierror


class ClientGUI:
	def __init__(self, parent):
		self.parent = parent
		self.parent.title("Chat App")
		self.parent.geometry("250x400")
		self.parent.resizable(False, False)
		self.client = None
		self.messages = []

		self.UsernameLabel = tk.Label(self.parent, text="Username:", font=("Arial", 16, "bold"))
		self.UsernameEntry = tk.Entry(self.parent)

		### REMOVE ###
		self.UsernameEntry.insert(0, "Aashir")


		self.PortLabel = tk.Label(self.parent, text="Port:", font=("Arial", 16, "bold"))
		self.PortEntry = tk.Entry(self.parent)
		self.PortEntry.insert(0, "5050")

		self.PasswordLabel = tk.Label(self.parent, text="Server Password:", font=("Arial", 16, "bold"))
		self.PasswordEntry = tk.Entry(self.parent, show="*")

		self.ServerHostNameLabel = tk.Label(self.parent, text="Server Host Name:", font=("Arial", 16, "bold"))
		self.ServerHostNameEntry = tk.Entry(self.parent)
		self.ServerHostNameEntry.insert(0, gethostname())

		self.JoinButton = tk.Button(self.parent, text="Join Server", width=20, height=3, command=self.join_server)

		self.UsernameLabel.pack()
		self.UsernameEntry.pack(pady=10, ipady=5)

		self.PortLabel.pack()
		self.PortEntry.pack(pady=10, ipady=5)

		self.PasswordLabel.pack()
		self.PasswordEntry.pack(pady=10, ipady=5)

		self.ServerHostNameLabel.pack()
		self.ServerHostNameEntry.pack(pady=10, ipady=5)

		self.JoinButton.pack()

	def join_server(self):
		username = self.UsernameEntry.get()
		port = self.PortEntry.get()
		server_password = self.PasswordEntry.get()
		server_host_name = self.ServerHostNameEntry.get()
		server_ips = None

		if not server_host_name or server_host_name == gethostname():
			server_ip = gethostbyname_ex(server_host_name)[-1][-1]

		else:
			try:
				server_ips = gethostbyname_ex(server_host_name)[-1]

			except gaierror:
				return

			if len(server_ips) == 1:
				server_ip = server_ips[0]
				server_ips = None

		if not username:
			return

		elif not port:
			port = 5050

		try:
			port = int(port)

		except ValueError:
			return

		if server_ips is not None:
			for server_ip in server_ips:
				self.client = Client(username, server_ip, port=port, server_pass=server_password)
				connected = self.client.join_server()
				
				if connected:
					break

			else:
				return

		else:
			self.client = Client(username, server_ip, port=port, server_pass=server_password)
			connected = self.client.join_server()

			if not connected:
				return

		for widget in self.parent.winfo_children():
			widget.destroy()

		self.parent.geometry("400x500")

		self.ChatListbox = tk.Listbox(self.parent, width=50, height=25)
		self.ChatScrollbar = tk.Scrollbar(self.parent)
		self.ChatText = tk.Text(self.parent, height=1, width=30)
		self.SendButton = tk.Button(self.parent, text="Send", width=20, height=2, font=("Arial", 8, "bold"))
		self.chat_updater = tk.Toplevel(self.parent)
		self.chat_updater.withdraw()

		self.SendButton.config(command=self.send_message)
		self.ChatText.bind("<Return>", lambda event: self.send_message())
		self.ChatListbox.config(yscrollcommand=self.ChatScrollbar.set)
		self.ChatScrollbar.config(command=self.ChatListbox.yview)

		self.ChatScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		self.ChatListbox.pack(pady=10)
		self.ChatText.pack()
		self.SendButton.pack(pady=10)

		# When the "x" in the top right is clicked, call self.quit
		self.parent.protocol("WM_DELETE_WINDOW", self.quit)
		self.update_chat_listbox()

	def update_chat_listbox(self):
		self.ChatListbox.delete(0, tk.END)

		for message in self.client.messages:
			self.ChatListbox.insert(tk.END, message)

		if not self.client.connected:
			self.quit()

		try:
			self.ChatListbox.delete(0, tk.END)

			for message in self.client.messages:
				self.ChatListbox.insert(tk.END, message)


			ServerGUI.color_code_listbox(self.ChatListbox)

		
		# When trying to close window
		except TclError:
			return

		self.chat_updater.after(10, self.update_chat_listbox)

	def send_message(self):
		message = self.ChatText.get("1.0", tk.END).strip("\n")
		if message == "get":
			print (self.client.messages)
			return
			
		self.ChatText.delete("1.0", tk.END)
		self.ChatText.see("1.0")

		self.client.send_message(message)

	def quit(self):
		if self.client is not None:
			self.client.close()

		self.parent.destroy()
		quit()
		
if __name__ == "__main__":
	parent = tk.Tk()
	ClientGUI(parent)
	parent.mainloop()
