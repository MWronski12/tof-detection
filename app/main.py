from csv_collector import CSVCollector
from tcp_collector import TCPCollector

from controller import Controller

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TMF8828 data client for detecting bicycles.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--tcp",
        type=str,
        help="ip:port of the tmf8828 tcp server",
    )
    group.add_argument(
        "--csv",
        type=str,
        help="path to tmf8828 csv file",
    )
    parser.add_argument(
        "--live-mode",
        action="store_true",
        default=False,
        help="Simulate live data from csv file (default is false)",
    )
    parser.add_argument(
        "--start-time",
        type=int,
        help="Epoch timestamp in milliseconds to start reading from (only for csv files)",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    controller = Controller()

    if args.csv:
        file_path = args.csv
        print(f"Reading from CSV file: {file_path}")
        collector = CSVCollector(
            mediator=controller,
            file_path=file_path,
            live_mode=args.live_mode,
            start_time=args.start_time,
        )

    elif args.tcp:
        host, port_str = args.tcp.split(":")
        port = int(port_str)
        print(f"Connecting to TCP server at {host}:{port}")
        collector = TCPCollector(
            mediator=controller,
            host=host,
            port=port,
        )

    controller.set_collector(collector)
    controller.start()


if __name__ == "__main__":
    main()
