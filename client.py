#!/usr/bin/python3

import socket
import struct
import time

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

MAX_DIST_MM = 3400
plot_data = []

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    t_start = time.time()
    while True:
        data = s.recv(4)
        if not data:
            print("Connection closed!")
            break

        # Convert the received data from network byte order to host byte order
        dist_mm = struct.unpack("!i", data)[0]

        if len(plot_data) > 1:
            plot_data.append((time.time() - t_start, dist_mm))
        else:
            plot_data.append((time.time() - t_start, dist_mm))

        if len(plot_data) == 100:
            print("======= PLOT DATA =======")
            for i in range(len(plot_data)):
                print("{:3.5}".format(plot_data[i][0]) + f" : {plot_data[i][1]}")
            print("=========================")
            plot_data = []
