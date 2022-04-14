import argparse
import socket
import time
import threading
from queue import Queue


def scan_tcp(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((address, port))
            print('TCP Port is open:', port)
        except:
            pass


def scan_udp(address, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_ICMP) as s:
        try:
            s.sendto(b'test', (address, port))
            s.recvfrom(1024)
        except socket.timeout:
            print("UDP Port Open:", str(port))
        except:
            pass


def parse():
    parser = argparse.ArgumentParser(usage="python3 {SCRIPT file_name}-s [FIRST PORT_NUMBER] -f [FINAL]"
                                           " -tcp -udp [NOT REQUIRED]",
                                     description="Check host's open ports; "
                                                 "if type is not mentioned, both will be checked")
    parser.add_argument('host_name', type=str)
    parser.add_argument('-s', default=1, type=int, help='Нижняя граница сканируемых портов')
    parser.add_argument('-f', default=2000, type=int, help='Верхняя граница сканируемых портов')
    parser.add_argument('-tcp', action='store_true', help='TCP порты')
    parser.add_argument('-udp', action='store_true', help='UDP порты')
    args = parser.parse_args()
    if not args.tcp and not args.udp:
        args.tcp = args.udp = True
    return args


def resolve():
    address = socket.gethostbyname(parse().host_name)
    print('Starting scan on host: ', address)
    if parse().tcp:
        scan_in_threads(scan_tcp, address)
    if parse().udp:
        scan_in_threads(scan_udp, address)


def scan_in_threads(scan, ip):
    socket.setdefaulttimeout(1)
    q = Queue()
    start_time = time.time()

    def threader():
        while True:
            port_num = q.get()
            scan(ip, port_num)
            q.task_done()

    for x in range(100):
        t = threading.Thread(target=threader)
        t.daemon = True
        t.start()

    for port in range(parse().s, parse().f):
        q.put(port)

    q.join()
    print('Time taken for {}'.format(scan.__name__), time.time() - start_time)


if __name__ == "__main__":
    socket.setdefaulttimeout(1)
    resolve()
