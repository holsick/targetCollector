#!/usr/bin/python3

import os
import sys
import os.path
import requests
from colorama import Fore, Style
from optparse import OptionParser
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

alive200 = []
alive301 = []
alive302 = []
userAgent = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}

def processDomainList(wordlist, timeout=3.0):
    if os.path.isfile(wordlist):
        with open(wordlist, 'r') as f:
            for subdomain in f.readlines():
                subdomain = subdomain.strip()
                try:
                    request = requests.get(
                        'https://' + subdomain,
                        timeout=timeout,
                        headers=userAgent,
                        allow_redirects=False,
                        verify=False
                    )
                    if request.status_code == 200:
                        print(f'{Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}] ' + subdomain + ' : ' + Fore.GREEN + str(request.status_code))
                        alive200.append('https://' + subdomain)
                    elif request.status_code == 301:
                        print(f'{Fore.WHITE}[{Fore.MAGENTA}*{Fore.WHITE}] ' + subdomain + ' : ' + Fore.MAGENTA + str(request.status_code) + ' -> ' + Fore.GREEN + request.headers.get('location') + Fore.WHITE)
                        alive301.append('https://' + subdomain + ' -301-> ' + request.headers.get('location'))
                    elif request.status_code == 302:
                        print(f'{Fore.WHITE}[{Fore.BLUE}*{Fore.WHITE}] ' + subdomain + ' : ' + Fore.BLUE + str(request.status_code) + ' -> ' + Fore.GREEN + request.headers.get('location') + Fore.WHITE)
                        alive302.append('https://' + subdomain + ' -302-> ' + request.headers.get('location'))
                    elif request.status_code == 403:
                        print(f'{Fore.WHITE}[{Fore.YELLOW}*{Fore.WHITE}] ' + subdomain + ' : ' + Fore.YELLOW + str(request.status_code))
                except requests.exceptions.ConnectionError:
                    if not options.silent:
                        print(f'{Fore.WHITE}[{Fore.YELLOW}-{Fore.WHITE}] {Fore.YELLOW}Request timed out.{Fore.WHITE} Trying http')
                    try:
                        request = requests.get(
                            'http://' + subdomain,
                            headers=userAgent,
                            allow_redirects=False,
                            timeout=timeout
                        )
                        if request.status_code == 200:
                            print(subdomain + ' : ' + str(request.status_code))
                            alive200.append('http://' + subdomain)
                    except requests.exceptions.ConnectionError:
                        if not options.silent:
                            print(f'[{Fore.RED}*{Fore.WHITE}] {Fore.RED} ' + subdomain + f'{Fore.WHITE} did not respond. Moving on')
                            pass
                except Exception as e:
                    if not options.silent:
                        print(f'{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] Read timed out. {subdomain} may not exist ' + str(e))
                        pass
    else:
        wordlist = wordlist.strip('\n')
        with open('temp.txt', 'w+') as _f:
            _f.write(wordlist)
        with open('temp.txt', 'r') as __f:
            for subdomain in __f.readlines():
                subdomain = subdomain.strip()
                try:
                    request = requests.get(
                        'https://' + subdomain,
                        headers=userAgent,
                        timeout=timeout,
                        allow_redirects=False,
                        verify=False
                    )
                    if request.status_code == 200:
                        print(f'{Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}] ' + subdomain + ' : ' + Fore.GREEN + str(request.status_code))
                        alive200.append('https://' + subdomain)
                    elif request.status_code == 301:
                        print(f'{Fore.WHITE}[{Fore.MAGENTA}*{Fore.WHITE}] ' + subdomain + ' : ' + Fore.MAGENTA + str(request.status_code) + ' -> ' + Fore.GREEN + request.headers.get('location') + Fore.WHITE)
                        alive301.append('https://' + subdomain + ' -301-> ' + request.headers.get('location'))
                    elif request.status_code == 302:
                        print(f'{Fore.WHITE}[{Fore.BLUE}*{Fore.WHITE}] ' + subdomain + ' : ' + Fore.BLUE + str(request.status_code) + ' -> ' + Fore.GREEN + request.headers.get('location') + Fore.WHITE)
                        alive302.append('https://' + subdomain + ' -302-> ' + request.headers.get('location'))
                    elif request.status_code == 403:
                        print(f'{Fore.WHITE}[{Fore.YELLOW}*{Fore.WHITE}] ' + subdomain + ' : ' + Fore.YELLOW + str(request.status_code))
                except requests.exceptions.ConnectionError:
                    if not options.silent:
                        print(f'{Fore.WHITE}[{Fore.YELLOW}-{Fore.WHITE}] {Fore.YELLOW}Request timed out.{Fore.WHITE} Trying http')
                    try:
                        request = requests.get(
                            'http://' + subdomain,
                            headers=userAgent,
                            allow_redirects=False,
                            timeout=timeout
                        )
                        if request.status_code == 200:
                            print(f'{Fore.WHITE}[{Fore.GREEN}+{Fore.WHITE}] ' + subdomain + ' : ' + Fore.GREEN + str(request.status_code))
                            alive200.append('http://' + subdomain)
                    except requests.exceptions.ConnectionError:
                        if not options.silent:
                            print(f'{Fore.WHITE}[{Fore.RED}*{Fore.WHITE}]{Fore.RED} ' + subdomain + f'{Fore.WHITE} did not respond. Moving on')
                            pass
                except Exception:
                    if not options.silent:
                        print(f'{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] Read timed out. {subdomain} may not exist')
                        pass
    with open(options.outfile, 'w+') as ___f:
        for target in (alive200 + alive301 + alive302):
            ___f.write(target + '\n')
    if os.path.exists('temp.txt'):
        os.remove('temp.txt')

def main():
    if not options.outfile:
        print(f'{Fore.WHITE}[{Fore.RED}!{Fore.WHITE}] Please specify an output file\n')
        parser.print_help()
        sys.exit()
    if not options.wordlist:
        wordlist = sys.stdin.read()
        processDomainList(wordlist)
    elif options.wordlist:
        wordlist = options.wordlist
        processDomainList(wordlist)

if __name__ == '__main__':
    usage = f"""
    {Style.BRIGHT}\n[{Fore.YELLOW}*{Fore.WHITE}] python3 targetCollector.py -w /path/to/wordlist -o targets.txt
[{Fore.YELLOW}*{Fore.WHITE}] targetCollector -w /path/to/wordlist -s -o targets.txt
[{Fore.YELLOW}*{Fore.WHITE}] amass enum -d example.com -o subdomains.txt && cat subdomains.txt | targetCollector -s -o targets.txt
    """
    parser = OptionParser(usage=usage)
    parser.add_option('-w', '--wordlist', type='string', dest='wordlist', help='File containing a list of subdomains -- (sub-domain.example.com)')
    parser.add_option('-s', '--silent', action='store_true', dest='silent', default=False, help='Only show live domains')
    parser.add_option('-o', '--outfile', type='string', dest='outfile', help='File to write target list to')
    (options, args) = parser.parse_args()
    main()