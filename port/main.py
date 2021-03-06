import argparse
import socket
import time
import threading
import urllib.request
import urllib.error
from queue import Queue


def get_address(arg):
    def test_connection():
        try:
            return urllib.request.urlopen('http://google.com/', timeout=10)
        except:
            print("Нет соединения")

    if test_connection() is not None:
        try:
            return socket.gethostbyname(arg)
        except:
            print("Невозможно разрешить доменное имя")
    else:
        return


def scan_tcp(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3)
        try:
            s.connect((address, port))
            print('TCP Port is open:', port)
        except:
            pass


def scan_udp(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(3)
        try:
            s.sendto(b'\x00' * 64, (address, port))
            data, _ = s.recvfrom(512)
            print("UDP Port Open:", str(port))
        except socket.error:
            pass


def parse():
    parser = argparse.ArgumentParser(usage="python3 {SCRIPT file_name}-s [FIRST PORT_NUMBER] -f [FINAL]"
                                           " -tcp -udp [NOT REQUIRED]",
                                     description="Check host's open ports; "
                                                 "if type is not mentioned, both will be checked")
    parser.add_argument('host_name', type=str)
    parser.add_argument('-s', default=1, type=int, help='Нижняя граница сканируемых портов')
    parser.add_argument('-f', default=100, type=int, help='Верхняя граница сканируемых портов')
    parser.add_argument('-tcp', action='store_true', help='TCP порты')
    parser.add_argument('-udp', action='store_true', help='UDP порты')
    args = parser.parse_args()
    if not args.tcp and not args.udp:
        args.tcp = args.udp = True
    return args


def scan_in_threads(scan, ip):
    socket.setdefaulttimeout(1)
    q = Queue()
    start_time = time.time()

    def threader():
        while True:
            port_num = q.get()
            scan(ip, port_num)
            q.task_done()

    for _ in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    for port in range(parse().s, parse().f):
        q.put(port)

    q.join()
    print('Time taken for {}'.format(scan.__name__), time.time() - start_time)


def resolve():
    address = get_address(parse().host_name)
    if address != None:
        print('Starting scan on host: ', address)
        if parse().tcp:
            scan_in_threads(scan_tcp, address)
        if parse().udp:
            scan_in_threads(scan_udp, address)


if __name__ == "__main__":
    resolve()
