from csv_collector import CSVCollector
from tcp_collector import TCPCollector

from controller import Controller


def main():
    controller = Controller()

    file_path = "out/data-1717278380.csv"
    collector = CSVCollector(mediator=controller, file_path=file_path)

    # host = "192.168.1.57"
    # port = 8080
    # collector = TCPCollector(mediator=controller, host=host, port=port)

    controller.set_collector(collector)
    controller.start()


if __name__ == "__main__":
    main()
