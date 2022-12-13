from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import requests

APPS = []

def download(link):
	res = requests.get(link + '/download?from=details', headers={
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.5 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.5'
		}).text
	soup = BeautifulSoup(res, "html.parser").find('a', {'id':'download_link'})
	if soup['href']:
		r = requests.get(soup['href'], stream=True, headers={
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.5 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.5'
		})
		with open(link.split('/')[-1] + '.apk', 'wb') as file:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					file.write(chunk)

def search(query):
	res = requests.get('https://m.apkpure.com/search?q={}&region='.format(quote_plus(query)), headers={
			'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.5 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.5',
			"Accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		}).text
	print(res)
	soup = BeautifulSoup(res, "html.parser")
	#for i in soup.findAll(lambda tag: tag and len(tag.attrs) >= 1 and "data-dt-app" in tag.keys() and "href" in tag.keys()):
	#for i in soup.select("[data-dt-app]"):
	for i in soup.findAll(attrs={"data-dt-app": True, 'href' : True}):
		APPS.append((i['href'],
					'https://d.apkpure.com/b/APK/' + i['data-dt-app'] + "?version=latest" ))
	print("APPS")
	print(APPS)


import cloudscraper
def search2(query):
	scraper = cloudscraper.create_scraper(delay=10,   browser={'custom': 'ScraperBot/1.0',})
	url = 'https://m.apkpure.com/search?q={}&region='.format(quote_plus(query))
	req = scraper.get(url)

	soup = BeautifulSoup(req.content,'lxml')
	#for i in soup.findAll(lambda tag: tag and len(tag.attrs) >= 1 and "data-dt-app" in tag.keys() and "href" in tag.keys()):
	#for i in soup.select("[data-dt-app]"):
	for i in soup.findAll(attrs={"data-dt-app": True, 'href' : True}):
		APPS.append((i['data-dt-app'],
					'https://d.apkpure.com/b/APK/' + i['data-dt-app'] + "?version=latest" ))
	return APPS

def download2(app, url):
	scraper = cloudscraper.create_scraper(delay=10,   browser={'custom': 'ScraperBot/1.0',})
	req = scraper.get(url)

	with open(app+".apk", 'wb') as f:
		f.write(req.content)

	return app+".apk"

import re
import json

PATTERNS = [('ip',r'((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'),
	('url',r'(^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*))'),
	('host',r'(((?!-)[A-Za-z0-9-]{1, 63}(?<!-)\\.)+[A-Za-z]{2, 6})')]

import pprint
pp = pprint.PrettyPrinter(indent=4)

def find_patterns(filename):
	print("processing %s" % filename)
	result={}
	for key, pattern in PATTERNS:
		result[key] = [re.findall(pattern,line) 
            for line in open(filename)]

	# Trim empties
	result = {k: [i for i in v if i] for k, v in result.items()}
	pp.pprint(result)

	with open(filename+".patterns", 'w') as f:
		f.write(json.dumps(result))

import sys

import os, subprocess

def strings(filename):
	os.system("strings %s > %s.strings" % (filename, filename))
	return filename+".strings"

if __name__ == '__main__':
    for app,url in search2(sys.argv[1]):
        print(app)
        filename = download2(app, url)
        strings_fn = strings(filename)
        find_patterns(strings_fn)
