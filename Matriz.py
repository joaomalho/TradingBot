#!/usr/bin/env python3

__version__ = 'v1.0'

try:
    import sys
    from colorama import Fore, Style
    import atexit
    import argparse
    import random
except KeyboardInterrupt:
    print('[!] Exiting.')
    sys.exit()
except:
    print('[!] Missing requirements. Try running python3 -m pip install -r requirements.txt')
    sys.exit()

def banner():
    print("                      __  __       _        _            ")
    print("   ___ /____/___     |  \/  | __ _| |_ _ __(_)____       ")
    print("  ___ /____/___      | |\/| |/ _` | __| '__| |_  /       ")
    print("     /    /          | |  | | (_| | |_| |  | |/ /        ")
    print("                     |_|  |_|\__,_|\__|_|  |_/___|       ")
    print("     Tranding AI Bot                     ")
    print("                                         ")
    print(" Matriz Ver. {}".format(__version__))
    print(" Coded by João Malho aka XaU")
    print("\n")

banner()

if sys.version_info[0] < 3:
    print("\033[1m\033[93m(!) Please run the tool using Python 3" + Style.RESET_ALL)
    sys.exit()

parser = argparse.ArgumentParser(description=
    "Advanced information gathering tool for matriz tool (https://github.com/joaomalho/Matriz) version {}".format(__version__),
                                 usage='%(prog)s -n <number> [options]')

parser.add_argument('-n', '--number', metavar='number', type=str,
                    help='The phone number to scan (E164 or international format)')

parser.add_argument('-i', '--input', metavar="input_file", type=argparse.FileType('r'),
                    help='Phone number list to scan (one per line)')

parser.add_argument('-o', '--output', metavar="output_file", type=argparse.FileType('w'),
                    help='Output to save scan results')

parser.add_argument('-s', '--scanner', metavar="scanner", default="all", type=str,
                    help='The scanner to use')

parser.add_argument('--osint', action='store_true',
                    help='Use OSINT reconnaissance')

parser.add_argument('-u', '--update', action='store_true',
                    help='Update the project')

args = parser.parse_args()