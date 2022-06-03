import struct


class DNSMessageParser:
    def __init__(self, data):
        self._data = data
        self._header = self.parse_header()
        int_flags = bin(self._header[1])
        self._flags = '0' * (16 - len(int_flags) + 2) + str(int_flags)[2:]
        self.answer = self._flags[0]
        self.name, self.q_type, position = self.parse_question()
        self._question_len = position
        self.info = self.parse_body(position)

    def parse_header(self):
        """
        +------------+
        |   Header   |
        +------------+
        """
        # H - 2 bytes
        header = struct.unpack('>6H', self._data[0:12])
        return header

    def parse_question(self):
        """
        +------------+
        |  Question  |
        +------------+
        """
        name, end = self.parse_domain(12)
        # H - 2 bytes
        qr_type, _ = struct.unpack('>HH', self._data[end: end + 4])
        information = f'Queries: name {name}, type {qr_type}'
        print(information)
        return name, qr_type, end + 4

    def parse_body(self, start):
        """
        +------------+
        |   Answer   |
        +------------+
        |  Authority |
        +------------+
        | Additional |
        +------------+
        """
        if self.answer:
            answer, an_offset = self.parse_r(start, 3)
            authority, au_offset = self.parse_r(an_offset, 4)
            additional, _ = self.parse_r(au_offset, 5)
            if answer:
                for e in answer:
                    print(f'\tname {e[0]}, type {e[1]},  value{e[3]}')
            if authority:
                for e in authority:
                    print(f'\tname {e[0]}, type {e[1]},  value{e[3]}')
            if additional:
                for e in additional:
                    print(f'\tname {e[0]}, type {e[1]},  value{e[3]}')
            return answer + authority + additional
        return None

    def parse_r(self, offset, index):
        rr_list = []
        for i in range(self._header[index]):
            name, end = self.parse_domain(offset)
            offset = end
            # I - 4 bytes
            # > - big
            # B - 1 byte
            r_type, r_class, r_ttl, rd_length = struct.unpack('>2HIH', self._data[offset: offset + 10])
            offset += 10
            if r_type == 1:
                ip = struct.unpack('>4B', self._data[offset: offset + 4])

                offset += 4
                rr_list.append((name, r_type, r_ttl, ip))
            elif r_type == 2:
                dns_server_name, dns_name_end = self.parse_domain(offset)
                offset = dns_name_end
                rr_list.append((name, r_type, r_ttl, dns_server_name))
            else:
                offset += rd_length
        return rr_list, offset

    def parse_domain(self, start):
        domain_list = []
        position = start
        end_position = start
        flag = False
        while True:
            if self._data[position] >= 64:
                if not flag:
                    end_position = position + 2
                    flag = True
                position = ((self._data[position] - 192) << 8) + self._data[position + 1]
                continue
            else:
                length = self._data[position]
                if length == 0:
                    if not flag:
                        end_position = position + 1
                    break
                position += 1
                domain_list.append(self._data[position: position + length])
                position += length
        name = '.'.join([i.decode('ascii') for i in domain_list])
        return name, end_position

    def make_answer(self, ttl, value):
        length = 0
        item = b''
        header = list(self._header[:12])
        header[1] = 2 ** 15
        header[3] = 1
        question = self._data[12: self._question_len]
        name = self._data[12: self._question_len - 4]

        # r_Type A
        if self.q_type == 1:
            item = b''
            for e in value:
                item += e.to_bytes(1, byteorder='big')
            length = 4

        # r_Type NS
        elif self.q_type == 2:
            octets = (name.decode()).split('.')
            result = []
            for octet in octets:
                result.append(len(octet))
                for b in octet:
                    result.append(ord(b))
            result.append(0)

            item = b''
            for e in result:
                item += e.to_bytes(1, byteorder='big')
            length = len(item)

        tail = b''
        d = [self.q_type, 1, ttl, length]
        for i, e in enumerate(d):
            if i == 2:
                tail += e.to_bytes(4, byteorder='big')
            else:
                tail += e.to_bytes(2, byteorder='big')

        answer = b''
        for e in header:
            answer += e.to_bytes(2, byteorder='big')
        answer += question + name + tail + item
        return answer
