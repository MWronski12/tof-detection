import numpy as np

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation


INTERVAL = 20


def do_plot_depth_map(data_provider, fig, ax, interval=INTERVAL):
    # Create a placeholder image
    zone_distances = np.zeros((3, 3))

    im = ax.imshow(
        zone_distances,
        cmap="autumn",
        extent=[0, 3, 3, 0],
        vmin=0,
        vmax=5000,
    )

    # Create the colorbar outside of the run method
    fig.colorbar(im, ax=ax, orientation="vertical")

    ax.set_title("Depth map")
    ax.set_xticks(np.arange(0, zone_distances.shape[1] + 1, 1))
    ax.set_yticks(np.arange(0, zone_distances.shape[0] + 1, 1))
    ax.grid(True, linestyle="--")

    def run(i):
        zone_distances = data_provider.get_zone_distances()
        if zone_distances is None:
            return

        # Update the data of the image
        im.set_data(zone_distances)

        # Clear the previous text
        for text in ax.texts:
            text.remove()

        # Add new text
        for i in range(zone_distances.shape[0]):
            for j in range(zone_distances.shape[1]):
                ax.text(j + 0.5, i + 0.5, zone_distances[i, j], ha="center", va="center")

    return FuncAnimation(fig, run, interval=interval, save_count=1024)


def do_plot_center_zones(data_provider, fig, ax, interval=INTERVAL, time_span_s=5, y_span_mm=6000):
    props = dict(boxstyle="round", facecolor="wheat", alpha=0.5)
    plt.rcParams["animation.html"] = "jshtml"

    ax.set_title("Center zone")
    ax.set(xlabel="time [s]", ylabel="distance [mm]")
    ax.set_xlim(0, time_span_s)
    ax.set_ylim(0, y_span_mm)
    ax.grid(True)
    scatter = ax.scatter([0], [0], color="orange", s=20)

    distance_box = ax.text(
        0.5,
        0.96,
        str(0),
        transform=ax.transAxes,
        fontsize=36,
        horizontalalignment="center",
        verticalalignment="top",
        bbox=props,
    )

    def run(i):
        data = data_provider.get_center_zone_data()
        if data is None or len(data[0]) < 2:
            return

        t_now = data[-1][0]
        left = t_now - time_span_s / 2
        right = t_now + time_span_s / 2
        ax.set_xlim(left, right)

        scatter.set_offsets(data)
        distance_box.set_text(f"{int(data[-1][1])} mm")

    return FuncAnimation(fig, run, interval=interval, save_count=1024)
