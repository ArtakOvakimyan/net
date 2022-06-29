import argparse
import socket
import datetime

PORT_NUM = 200


def get_time_offset():
    with open('config.txt', 'r') as config:
        try:
            return int(config.read())
        except Exception:
            raise Exception("There must be an integer value")


def get_time(offset):
    real_time = datetime.datetime.now()
    return str(real_time + datetime.timedelta(0, offset))


def start_server(offset):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('127.0.0.1', PORT_NUM))
        while True:
            data, addr = sock.recvfrom(1024)
            time = get_time(offset)
            sock.sendto(time.encode('utf-8'), addr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(usage="print '$sudo python3 {SCRIPT file_name}' to start",
                                     description="A simple lying time-server, working with a client-script")

    start_server(get_time_offset())
