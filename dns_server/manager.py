import socket
from cacher import Cacher
from parser import DNSMessageParser

BIG_BROTHER = "8.8.8.8"


class DNSManager:
    def __init__(self, cache: Cacher):
        self.cache = cache
        self.host_ip = get_host_ip()

    def start(self):
        print("IPV4: ", self.host_ip)
        while True:
            self.handle_request()
            self.cache.dump_cache()

    def handle_request(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as dns_sock:
            dns_sock.bind((self.host_ip, 53))
            data, client_address = dns_sock.recvfrom(1024)
            request = DNSMessageParser(data)
            answer = self.get_from_cache(request)

            if answer is None:
                answer = self.get_from_BIG_BROTHER(data)
                self.add_in_cache(answer)
            dns_sock.sendto(answer, client_address)

    def get_from_BIG_BROTHER(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as aux_sock:
            aux_sock.bind((self.host_ip, 4))
            aux_sock.sendto(data, (BIG_BROTHER, 53))
            answer = aux_sock.recvfrom(1024)[0]
        return answer

    def get_from_cache(self, request: DNSMessageParser):
        answer_from_cache = self.cache.get_record(
                (request.name, request.q_type))
        if answer_from_cache is None:
            return None
        value = answer_from_cache[0]
        ttl = answer_from_cache[2]
        return request.make_answer(ttl, value)

    def add_in_cache(self, data):
        answer = DNSMessageParser(data)
        for info in answer.info:
            self.cache.add_record(*info)


def get_host_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect((BIG_BROTHER, 80))
        return sock.getsockname()[0]
