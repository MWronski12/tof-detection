from csv_collector import CSVCollector
from tcp_collector import TCPCollector

from controller import Controller

def main():
    file_path = "out/data-1717252742.csv"
    collector = CSVCollector(file_path)
    
    # host = "192.168.1.57"
    # port = 8080
    # collector = TCPCollector(host=host, port=port)
    
    controller = Controller(collector)
    controller.start()

if __name__ == "__main__":
    main()
