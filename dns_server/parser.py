import struct


class Parser:
    def __init__(self, data):
        self.data = data
        self.header = self.parse_header()
        flags = bin(self.header[1])
        self.flags = '0' * (16 - len(flags) + 2) + str(flags)[2:]
        self.answer = self.flags[0]
        self.name, end_position = self.get_question_domain(12, 255)
        self.q_type, self.question_class = struct.unpack(">HH", self.data[end_position + 1: end_position + 5])
        self.length_of_question = end_position + 5
        self.info = self.parse_body(end_position + 5)

    def parse_header(self):
        """
        +------------+
        |   Header   |
        +------------+
        """
        header = struct.unpack('>6H', self.data[0:12])
        return header

    def parse_body(self, position):
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
            offset1, r_answer = self.get_recs(position, 3)
            offset2, r_authority = self.get_recs(offset1, 4)
            r_additional = self.get_recs(offset2, 5)[1]
            return r_answer + r_authority + r_additional
        return None

    def get_question_domain(self, offset, domain_length_in_bytes):
        state = 0
        domain_string = ''
        expected_length = 0
        domain_parts = []
        x = 0
        end_position = offset
        data = self.data[offset:offset + domain_length_in_bytes]
        has_offset = False
        for byte in data:
            if not byte:
                break
            if has_offset:
                has_offset = False
                end_position += 1
                continue
            if str(bin(byte))[2:4] == "11" and len(str(bin(byte))) == 10:
                name_offset = struct.unpack(">B", self.data[end_position + 1:end_position + 2])[0]
                has_offset = True
                domain, _ = self.get_question_domain(name_offset, 255)
                domain_parts.append(domain)
            else:
                if state == 1:
                    domain_string += chr(byte)
                    x += 1
                    if expected_length == x:
                        domain_parts.append(domain_string)
                        domain_string = ''
                        state = 0
                        x = 0
                else:
                    state = 1
                    expected_length = byte
            end_position += 1
        domain = ".".join(domain_parts)
        return domain, end_position

    def get_recs(self, start_index, index_in_header):
        list_of_records = []
        offset = start_index
        original_offset = offset
        flag = False
        for i in range(self.header[index_in_header]):
            print(self.data[offset:offset + 1])
            if self.data[offset:offset + 1] == b'':
                break
            is_off = struct.unpack(">B", self.data[offset:offset + 1])
            if str(bin(is_off[0]))[2:4] == "11":
                original_offset = offset + 2
                offset = struct.unpack(">B", self.data[offset + 1:offset + 2])[0]
                flag = True
            domain, end_position = self.get_question_domain(offset, 255)
            offset = end_position
            if flag:
                offset = original_offset
            record_type, record_class, record_ttl, record_length = struct.unpack(">2HIH", self.data[offset: offset + 10])
            offset += 10

            if record_type == 1:  # A
                domain_ip = struct.unpack(">4B", self.data[offset:offset + 4])
                offset += 4
                list_of_records.append((domain, record_type, record_ttl, 4, domain_ip))

            elif record_type == 2:  # NS
                dns_name, end_name_position = self.get_question_domain(offset, record_length)
                list_of_records.append((domain, record_type, record_ttl, end_name_position - offset, dns_name))
                offset = end_name_position

            else:
                offset += record_length
            flag = False
        return offset, list_of_records

    def pack_name(self, domain):
        if type(domain) == str:
            names = domain.split(".")
        else:
            names = (domain.decode('utf8')).split(".")
        res = []
        for name in names:
            res.append(len(name))
            for letter in name:
                res.append(ord(letter))
        res.append(0)
        return struct.pack(">" + str(len(res)) + "B", *res), len(res)

    def make_answer(self, info):
        header = list(self.header)
        header[1] += 32768
        header[3] = len(info)
        question = self.data[12:self.length_of_question]
        question_and_answer = question
        #A
        if self.q_type == 1:
            for record in info:
                offset = struct.pack(">2B", 192, 12)
                question_and_answer += offset + struct.pack(">HHIH", record[1], 1, record[2], 4) + struct.pack(">4B", *record[4])
        #NS
        if self.q_type == 2:
            for record in info:
                offset = struct.pack(">2B", 192, 12)
                pack_name = self.pack_name(record[4])
                question_and_answer += offset + struct.pack(">HHIH", record[1], 1, record[2], pack_name[1]) + pack_name[0]

        response = struct.pack(">6H", *header) + question_and_answer
        return response
