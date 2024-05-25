from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from threading import Lock, Thread
import socket
import struct
import time


HOST = "192.168.119.1"  # The server's hostname or IP address
PORT = 8080  # The port used by the server

X_SPAN = 5
Y_SPAN = 5000
MAX_LEN = 300


lock = Lock()
x_list = deque(maxlen=MAX_LEN)
y_list = deque(maxlen=MAX_LEN)
confidence_list = deque(maxlen=MAX_LEN)


def collect_data():
    global lock, x_list, y_list

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print("Successfully connected to data stream!")

        t_start = time.time()
        while True:
            bytes = s.recv(32)
            if not bytes:
                print("Connection closed!")
                break

            (
                timestamp_ms,
                ambient_light,
                confidence_target_0,
                distance_mm_target_0,
                confidence_target_1,
                distance_mm_target_1,
            ) = struct.unpack("<Qiiiiixxxx", bytes)

            dist_mm = max(distance_mm_target_0, distance_mm_target_1)

            lock.acquire()
            x_list.append(time.time() - t_start)
            y_list.append(dist_mm)
            lock.release()


def plot_data():
    global x_list, y_list, lock

    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    plt.rcParams["animation.html"] = "jshtml"
    fig, ax = plt.subplots()
    ax.set_title("TMF8828 camera")
    ax.set(xlabel="time [s]", ylabel="distance [mm]")
    ax.set_xlim(0, X_SPAN)
    ax.set_ylim(0, Y_SPAN)
    ax.grid(1)
    scatter = ax.scatter([0], [0], color="orange", s=20)

    distance_box = ax.text(
        0.9,
        0.9,
        str(0),
        transform=ax.transAxes,
        fontsize=40,
        horizontalalignment="right",
        verticalalignment="top",
        bbox=props,
    )

    def annotate(last_y):
        distance_box.set_text(f"{last_y:4d} mm")

    def run(i):
        lock.acquire()
        if len(x_list) == 0:
            lock.release()
            return

        ax.set_xlim(
            left=max(0, x_list[-1] - X_SPAN / 2),
            right=max(X_SPAN, x_list[-1] + X_SPAN / 2),
        )
        scatter.set_offsets([[x, y] for x, y in zip(x_list, y_list)])
        annotate(y_list[-1])
        lock.release()

    ani = FuncAnimation(fig, run, frames=60, interval=1 / 60.0 * 1000)
    plt.show()


def main():
    Thread(target=collect_data, daemon=True).start()
    plot_data()


if __name__ == "__main__":
    main()
