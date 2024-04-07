import socket
import struct
import time
import sys
import signal
from matplotlib import pyplot as plt
from typing import List, Tuple
import numpy as np

HOST = "192.168.185.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

data: List[Tuple[int, int]] = []


def signal_handler(signal, frame):
    plot_data()
    sys.exit(0)


def plot_data():
    # Extract x and y coordinates from the list of tuples
    x_values = [point[0] for point in data]
    y_values = [point[1] for point in data]

    # Plot the points
    plt.scatter(x_values, y_values, color="blue")
    plt.title("Scatter Plot of Points")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True)

    plt.show()


def do_collect_data() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Successfully connected to data stream!")

        t_start = time.time()
        while True:
            dist_mm_bytes = s.recv(4)
            if not dist_mm_bytes:
                print("Connection closed!")
                break

            # Convert the received data from network byte order to host byte order
            dist_mm = struct.unpack("!i", dist_mm_bytes)[0]
            print(dist_mm)
            data.append((time.time() - t_start, dist_mm))


def main() -> None:
    signal.signal(signal.SIGINT, signal_handler)
    do_collect_data()


if __name__ == "__main__":
    main()
