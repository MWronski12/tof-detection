#!/usr/bin/python3

import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    for i in range(5):
        data = s.recv(1024)
        if not data:
            print("Connection closed!")
            break

        print("Data received:", data)
    
