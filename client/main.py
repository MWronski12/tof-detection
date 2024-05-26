from live_data_provider import LiveDataProvider
from csv_data_provider import CSVDataProvider
from data_plotting import do_plot_center_zones, do_plot_depth_map

import matplotlib.pyplot as plt


HOST = "192.168.1.57"
PORT = 8080
SPAN = 192
INTERVAL = 1000 / 30

def main():
    # data_provider = LiveDataProvider(host=HOST, port=PORT)
    data_provider = CSVDataProvider(span=SPAN, file_path="out/test1.csv", interval=INTERVAL)

    fig, (ax1, ax2) = plt.subplots(1, 2)
    ani1 = do_plot_depth_map(data_provider, fig, ax1, interval=INTERVAL)
    ani2 = do_plot_center_zones(data_provider, fig, ax2, interval=INTERVAL)

    plt.show()


if __name__ == "__main__":
    main()
