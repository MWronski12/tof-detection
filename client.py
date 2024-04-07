import socket
import struct

HOST = "localhost"  # The server's hostname or IP address
PORT = 8080  # The port used by the server


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Successfully connected to data stream!")

        while True:
            dist_mm_bytes = s.recv(4)
            if not dist_mm_bytes:
                print("Connection closed!")
                break

            # Convert the received data from network byte order to host byte order
            dist_mm = struct.unpack("!i", dist_mm_bytes)[0]
            print(dist_mm)


if __name__ == "__main__":
    main()
