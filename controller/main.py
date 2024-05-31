from gui import GUI
from csv_collector import CSVCollector
from tcp_collector import TCPCollector
from message import Message

import threading


def main():
    file_path = "out/data-1717188733.csv"
    collector = CSVCollector(file_path)
    
    # host = "192.168.1.57"
    # port = 8080
    # collector = TCPCollector(host=host, port=port)
    
    gui = GUI()

    def callback(data):
        choose_zone_distances = lambda zone_data: (zone_data[1] if zone_data[0] >= zone_data[2] else zone_data[3])

        timestamp = data[0] / 1000.0
        measurements = data[2:]
        zone_distances = []
        for i in range(0, len(measurements), 4):
            zone_data = measurements[i : i + 4]
            zone_distances.append(choose_zone_distances(zone_data))

        gui.notify(Message(timestamp, zone_distances))

    collector.subscribe(callback)

    worker = threading.Thread(target=collector.start, daemon=True)
    worker.start()

    gui.start()


if __name__ == "__main__":
    main()
