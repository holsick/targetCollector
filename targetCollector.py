#!/usr/bin/python3

import os
import sys
import os.path
import requests
from colorama import Fore, Style
from optparse import OptionParser
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# colors
bright = Style.BRIGHT
w = Fore.WHITE
g = Fore.GREEN
b = Fore.BLUE
r = Fore.RED
y = Fore.YELLOW
m = Fore.MAGENTA

class TargetCollector:

	alive200, alive301, alive302 = [], [], []
	userAgent = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0'}

	def __init__(self, wordlist, outfile, silent=False, timeout=3.0):
		self.wordlist = wordlist
		self.timeout = options.timeout
		self.silent = options.silent
		self.outfile = options.outfile

	def processDomainlist(self):

		with open(self.wordlist, 'r') as f:
			for subdomain in f.readlines():
				subdomain = subdomain.strip()
				try:
					request = requests.get(
						'https://' + subdomain,
						timeout=self.timeout,
						headers=self.userAgent,
						allow_redirects=False,
						verify=False
					)

					if request.status_code == 200:
						print(f'{w}[{g}+{w}] ' + subdomain + ' : ' + g + str(request.status_code))
						self.alive200.append('https://' + subdomain)

					elif request.status_code == 301:
						print(f'{w}[{m}*{w}] ' + subdomain + ' : ' + m + str(request.status_code) + ' -> ' + g + request.headers.get('location') + w)
						self.alive301.append('https://' + subdomain + ' -301-> ' + request.headers.get('location'))

					elif request.status_code == 302:
						print(f'{w}[{b}*{w}] ' + subdomain + ' : ' + b + str(request.status_code) + ' -> ' + g + request.headers.get('location') + w)
						self.alive302.append('https://' + subdomain + ' -302-> ' + request.headers.get('location'))

					elif request.status_code == 403:
						print(f'{w}[{y}*{w}] ' + subdomain + ' : ' + y + str(request.status_code))

				# if SSL fails, lets try port 80 (http)
				except requests.exceptions.ConnectionError:
					if not self.silent:
						print(f'{w}[{y}-{w}] {y}Request timed out.{w} Trying http')

					try:
						request = requests.get(
							'http://' + subdomain,
                			timeout=self.timeout,
                			headers=self.userAgent,
                			allow_redirects=False
                		)
						if request.status_code == 200:
							print(f'{w}[{g}+{w}] ' + subdomain + ' : ' + g + str(request.status_code) + w)
							self.alive200.append('http://' + subdomain)

						elif request.status_code == 301:
							print(f'{w}[{m}*{w}] ' + subdomain + ' : ' + m + str(request.status_code) + ' -> ' + g + request.headers.get('location') + w)
							self.alive301.append('http://' + subdomain + ' -301-> ' + request.headers.get('location'))

						elif request.status_code == 302:
							print(f'{w}[{b}*{w}] ' + subdomain + ' : ' + b + str(request.status_code) + ' -> ' + g + request.headers.get('location') + w)
							self.alive302.append('http://' + subdomain + ' -302-> ' + request.headers.get('location'))

						elif request.status_code == 403:
							print(f'{w}[{y}*{w}] ' + subdomain + ' : ' + y + str(request.status_code))

					# if http also fails, assume the domain is dead
					except requests.exceptions.ConnectionError:
						if not self.silent:
							print(f'[{Fore.RED}*{Fore.WHITE}] {Fore.RED} ' + subdomain + f'{Fore.WHITE} did not respond. Moving on')
							pass

				except Exception as e:
					if not self.silent:
						print(f'{w}[{r}!{w}] Read timed out. {subdomain} may not exist ' + str(e))
						pass
		with open(self.outfile, 'w+') as _f:
			for target in (self.alive200 + self.alive301 + self.alive302):
				_f.write(target + '\n')

def main():
	if not options.outfile:
		print(f'{w}[{r}!{w}] Please specify an output file\n')
		parser.print_help()
		sys.exit()

	# if -w is not used, take data from stdin and create a temporary wordlist file
	if not options.wordlist:
		wordlist = sys.stdin.read()
		wordlist = wordlist.strip()
		with open('temp.txt', 'w+') as __f:
			__f.write(wordlist)

		# delete temporary file after finishing or user quits
		# having troubles deleting the file on Windows
		try:
			collector = TargetCollector('temp.txt', options.outfile, options.silent, options.timeout)
			collector.processDomainlist()
		except KeyboardInterrupt:
			if os.path.exists('temp.txt'):
				os.remove('temp.txt')

		if os.path.exists('temp.txt'):
			os.remove('temp.txt')
			
	# if -w, dont create temp file
	elif options.wordlist:
		collector = TargetCollector(options.wordlist, options.outfile, options.silent, options.timeout)
		collector.processDomainlist()


if __name__ == '__main__':
	# process command line options
	usage = f"""
    {bright}\n[{y}*{w}] python3 targetCollector.py -w /path/to/wordlist -o targets.txt
[{y}*{w}] targetCollector -w /path/to/wordlist -s -o targets.txt
[{y}*{w}] amass enum -d example.com -o subdomains.txt && cat subdomains.txt | targetCollector -s -o targets.txt
    """
	parser = OptionParser(usage=usage)
	parser.add_option('-w', '--wordlist', type='string', dest='wordlist', help='File containing a list of subdomains -- (sub-domain.example.com)')
	parser.add_option('-s', '--silent', action='store_true', dest='silent', default=False, help='Only show live domains')
	parser.add_option('-o', '--outfile', type='string', dest='outfile', help='File to write target list to')
	parser.add_option('-t', '--timeout', type=float, dest='timeout', help='http request timeout value (specify float value eg. 3.0)')
	(options, args) = parser.parse_args()
	
	main()
