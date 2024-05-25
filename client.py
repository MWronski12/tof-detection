import socket
import struct

HOST = "localhost"  # The server's hostname or IP address
PORT = 8080  # The port used by the server


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Successfully connected to data stream!")

        while True:
            bytes = s.recv(8 + 4 + 4 * 18 + 4 * 18 + 4)
            if not bytes:
                print("Connection closed!")
                break

            unpacked_data = struct.unpack("<Qi18i18i4x", bytes)
            timestamp_ms = unpacked_data[0]
            ambient_light = unpacked_data[1]
            confidences = unpacked_data[2:20]
            distances = unpacked_data[20:38]

            print(
                f"timestamp_ms: {timestamp_ms}\n"
                f"ambient_light: {ambient_light}\n"
                f"confidences: {confidences}\n"
                f"distances: {distances}\n"
            )


if __name__ == "__main__":
    main()
