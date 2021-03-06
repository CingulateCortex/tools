#!/usr/bin/python
# -*- coding: utf-8 -*-


__VERSION__ = '0.1'
__AUTHOR__ = 'Galkan'
__DATE__ = '30.10.2013'


try:
	import urllib2
	import sys
	import re
	import random
	import argparse
	import time
except ImportError,err:
     	import sys 
     	sys.stdout.write("%s\n" %err)
     	sys.exit(1)



class Crawl:

	def __init__(self, url_opt, mail_opt, time = 0):

		self.HEADERS = {
			'User-Agent': 'Mozilla/5.0',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate',
			'Connection': 'close',
			'DNT': '1'
		}

		self.UAS = [
			'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11',
			'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:17.0) Gecko/20100101 Firefox/17.0',
			'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17',
			'Mozilla/5.0 (Linux; U; Android 2.2; fr-fr; Desire_A8181 Build/FRF91) App3leWebKit/53.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1',
			'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; FunWebProducts; .NET CLR 1.1.4322; PeoplePal 6.2)',
			'Mozilla/5.0 (Windows NT 5.1; rv:13.0) Gecko/20100101 Firefox/13.0.1',
			'Opera/9.80 (Windows NT 5.1; U; en) Presto/2.10.289 Version/12.01',
			'Mozilla/5.0 (Windows NT 5.1; rv:5.0.1) Gecko/20100101 Firefox/5.0.1',
			'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 3.5.30729)'
    		]

		self.time = time
		self.url_opt = url_opt
		self.mail_opt = mail_opt

		self.url_reg = re.compile("href\s*=\s*\"([^\"]+)\"")
		if not self.mail_opt == "all":
			self.email_reg = re.compile("[\d\w\-\_\.]+@%s"% (self.mail_opt))
		else:
			self.email_reg = re.compile("[\d\w\-\_\.]+@[\d\w\-\_\.]+")
		self.site_reg = re.compile("(https?|ftp://)|(javascript|mailto)")


	def crawl(self, html):
		
		ret_list = []
		for node in html:
			if re.findall(self.url_reg, node):
				resp = re.findall(self.url_reg, node)
				for elem in resp:
					if not re.match(self.site_reg, elem):
						if not elem in ret_list:
							ret_list.append(elem)

		return ret_list


	def extract_email(self, html):

		email_res = []
		for node in html:
			if re.findall(self.email_reg, node):
				email = re.findall(self.email_reg, node)
				for node in email:
					if node not in email_res:
						email_res.append(node)

		return email_res


	def get_webpage(self, url):
	
		html = None		

		request = urllib2.Request(url)
		self.HEADERS['User-Agent'] = random.choice(self.UAS)
		request.add_header('User-Agent', self.HEADERS)

		response = urllib2.urlopen(request)
               	html = response.readlines()

		return html


	def main(self, url):

		hostname = url.split("/")[2]
		html = self.get_webpage(url)

		if not html == None:
			if self.url_opt == "url":
				response_list = self.extract_email(html)	
				for node in response_list:
					print node
			elif self.url_opt == "url-all":
				crawled_url = self.crawl(html)
				for url in crawled_url:
					new_url = ""
					if not re.match("/", url):
						new_url = "http://" + hostname + "/" + url
					else:
						new_url = "http://" + hostname + url

				email_list = []
				for url in crawled_url:
					new_url = ""
					if not re.match("/", url):
						new_url = "http://" + hostname + "/" + url
					else:
						new_url = "http://" + hostname + url

					html = self.get_webpage(new_url)
					response_list = self.extract_email(html)
					
					for node in response_list:
						if node and node not in email_list:
							email_list.append(node)

					if not self.time == 0:
						sleep_time = random.randint(1,int(self.time))
						time.sleep(sleep_time)

				for email_res in email_list:
					print email_res

		else:
			print "Error, Gettig Html Web Page !!!"
			sys.exit(3)


##
### Main ...
##

if __name__ == "__main__":

	parser = argparse.ArgumentParser(description='Email Crawler From Web Sites')
        g = parser.add_mutually_exclusive_group(required=True)

        g.add_argument('--url', dest='url', action='store_const', const='url', help="Only this url")
        g.add_argument('--url-all', dest='url', action='store_const', const='url-all', help="All the urls discovered")
	
	parser.add_argument('options', nargs=1)
	parser.add_argument('--mail', dest='mail', help="Email", required = True)
	parser.add_argument('--time', dest='time', help="Random Sleep Time")
	args = parser.parse_args()

	if not re.match("https?://",args.options[0]):
		print >> sys.stderr , "Url:  \"%s\"   must start with http(s) pattern !!!"% (args.options[0])
		sys.exit(2)

	if args.time:
		crawl = Crawl(args.url, args.mail, args.time)
	else:
		crawl = Crawl(args.url, args.mail, 0)
	crawl.main(args.options[0])
