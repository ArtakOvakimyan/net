import argparse
import json
import subprocess
import requests

"""
This script will provide you to route a trace to a hostname
by giving ip-address, country, AS number of transitional hosts

To use type: python3 {script_name} {host_name}
"""


def tracer(host_name) -> None:
    # here we use interface Popen to execute "traceroute"
    p = subprocess.Popen(['traceroute', host_name], stdout=subprocess.PIPE)
    # function "communicate" will send data to stdin from Popen of current process
    # and returns tuple of output and errors (stdout and stderr)
    out = p.communicate()[0].decode()
    for i in enumerate(out.split('\n')[1:-1], start=1):
        # pull ip-address
        ip = i[1].split()[2]

        # if 'out' was "* * *"
        if ip == '*':
            continue

        # parse, deleting braces
        ip = ip[1:-1]
        info = get_ip_info(ip)

        # print number-by-order and ip-address
        print(f'{i[0]}\t{ip}')

        # skip if it was not possible to get info from service
        if info is None:
            print()
        # else print info from json_response
        else:
            print(f'\thostname: {info["hostname"]}\n\tcountry: {info["country"]}\n'
                  f'\tAS and provider: {info["AS and provider"]}\n')


def get_ip_info(ip: str) -> dict:
    # fetch json from service "ipinfo.io"
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        content = json.loads(response.content)
        return {'hostname': content['hostname'],
                'country': content['country'],
                'AS and provider': content["org"]}
    except:
        pass


# parse to get terminal argument (hostname)
def parser() -> str:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("hostname", type=str)
    args = argument_parser.parse_args()
    return args.hostname


def main():
    tracer(parser())


if __name__ == '__main__':
    main()
