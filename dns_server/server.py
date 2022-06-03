from cacher import Cacher
from manager import DNSManager


def main():
    DNSManager(Cacher()).start()


if __name__ == '__main__':
    main()
