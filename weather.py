#!/usr/bin/python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup , SoupStrainer
from cookielib import CookieJar
from datetime import datetime, date, time

import re
import urllib2
import urllib
import codecs
import sys
import copy
import string

import WeatherForecast

###########

#constants
base_dir = "./"
namesFile = "./names.txt"
listFile = "index.html"

imgDomainMobile = "http://mobile.meteofrance.com/"
# header is geared toward iphone
head = u"""
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
	<meta name="viewport" content="width=350, user-scalable=yes">
	<link rel="stylesheet" href="/css/weather.css" type="text/css" />
"""
foot =u"""
	<div class="footer">
		Les pr&eacute;visions m&eacute;t&eacute;o sont extraites du site de M&eacute;t&eacute;o-France. Elles sont reproduites en accord avec les informations pr&eacute;sentes sur la page concernant les <a href="http://france.meteofrance.com/france/accueil/informations_publiques">informations publiques</a>.
	</div>
"""
#timeFormat = "%A %d %B %Y - %H:%M:%S " 
timeFormat = "%Y/%m/%d &agrave; %H:%M:%S " 

def getCityNameFrance(content):
	cityInfosFilter = SoupStrainer('div',{'class':'choix'})
	otherSoup=BeautifulSoup(content,parseOnlyThese=cityInfosFilter)
        infosPage = otherSoup("p",text=True)
	return infosPage[0].parent.text

def getCityNameMonde(content):
	cityInfosFilter = SoupStrainer('div',{'class':'infos'})
	otherSoup=BeautifulSoup(content,parseOnlyThese=cityInfosFilter)
	infosPage = otherSoup("p",text=True)
	return infosPage[0]
	
###########

def getWeatherContentHTML_monde(dico,content):
	domain = dico["domain"]
	suffix = dico["suffix"]	
	list = [u'']

	day=""
	indent="    "
	indent2=indent+indent

	cityInfosFilter = SoupStrainer('div',{'class':'infos'})
	otherSoup=BeautifulSoup(content,parseOnlyThese=cityInfosFilter)
	infosPage = otherSoup("p",text=True)
	#no post code on foreign cities
	cityName = infosPage[0]
	if len(infosPage) == 3 :
		lastUpdate = infosPage[2]
	else :
		#cityPostcode = infosPage[1]
		lastUpdate = infosPage[3]

	links = SoupStrainer('table',{'class':'tableWeather'})
	soup= BeautifulSoup(content, parseOnlyThese=links)

	pageName = u"Pr&eacute;visions m&eacute;t&eacute;o pour "+cityName+" ".encode('utf-8')

	title = u"<div class=\"content\">\n"
	title +=u"<h1>"+pageName+"</h1>\n".encode('utf-8')
	title +=u"<h3>R&eacute;cuper&eacute; le "+datetime.now().strftime(timeFormat)+"</h3>\n"

	source = getSourceSentence(domain+suffix,cityName)

	list.append(title)
	list.append(source)
	list.append(u"<h3>"+lastUpdate+"</h3>")
	list.append(u"<table>")

	for line in soup("tr"):
		period=""
		# for the last line
		if len(line) < 4 :
			continue
		# for the daily summary	
		if(line.__dict__['attrs'] != None and len(line.__dict__['attrs'])>0 ):
			s = str(line.attrs[0][1]).decode('iso-8859-1')
			n= s.find(" ")
                        
			if n>=0:
                                day = WeatherForecast.WeatherForecast()
                                day.loadWorldPeriod(line)
                                list.extend(day.toHTML())


			else:#summary of that day or empty line?
				sDay=s
				weather = line.contents[2]
				if len(weather.contents)==0:
					#for the first line
					continue
                                day = WeatherForecast.WeatherForecast()
                                day.loadWorldDay(line)
                                list.extend(day.toHTML())

	
	list.append(u"</table>\n<div>\n")
	return list
	
def parseMeteoPage(dico,content,tracking=""):
	name = dico["name"]
	domain = dico["domain"]
	suffix = dico["suffix"]	
	list = [u'']

	day=""
	indent="    "
	indent2=indent+indent

	cityInfosFilter = SoupStrainer('div',{'class':'infos'})
	otherSoup=BeautifulSoup(content,parseOnlyThese=cityInfosFilter)
	infosPage = otherSoup("p",text=True)
	#no post code on foreign cities
	cityName = infosPage[0]
	if len(infosPage) == 3 :
		lastUpdate = infosPage[2]
	else :
		#cityPostcode = infosPage[1]
		lastUpdate = infosPage[3]

	links = SoupStrainer('table',{'class':'tableWeather'})
	soup= BeautifulSoup(content, parseOnlyThese=links)

	pageName = u"Pr&eacute;visions m&eacute;t&eacute;o pour "+cityName+" ".encode('utf-8')

	title = u"<html>\n<head>"+head+"<title>"+pageName+"</title>\n</head>\n<body>\n"

	list.append(title)
	list.extend(getWeatherContentHTML_monde(dico,content))
	list.append(foot + u"<div class=\"nav\">Retourner &agrave <a href=\"/\">la list des villes</a></div>\n")
	list.append(tracking)
	list.append("</body>\n</html>")
	return list


def getWeatherContentHTML_france(dico,content):
	domain = dico["domain"]
	suffix = dico["suffix"]	
	list = [u'']

	day=""
	indent="    "
	indent2=indent+indent

	cityInfosFilter = SoupStrainer('div',{'class':'choix'})
	otherSoup=BeautifulSoup(content,parseOnlyThese=cityInfosFilter)
	infosPage = otherSoup("p",text=True)
	#no post code on foreign cities
	cityName = infosPage[0]
	
	if len(infosPage) == 3 :
		lastUpdate = infosPage[2]
	else :
		#cityPostcode = infosPage[1]
		lastUpdate = infosPage[3]

	pageName = u"Pr&eacute;visions m&eacute;t&eacute;o pour "+cityName+" ".encode('utf-8')
	title =u"<div class=\"content\">\n"
	title +=u"<h1>"+pageName+"</h1>\n".encode('utf-8')
	title +=u"<h3>R&eacute;cuper&eacute; le "+datetime.now().strftime(timeFormat)+"</h3>\n"

	source = getSourceSentence(domain+suffix,cityName)

	list.append(title)
	list.append(source)
	list.append(u"<h3>"+lastUpdate+"</h3>")
	list.append(u"<table>")


	# daily summaries
        daySummarylinks = SoupStrainer('dl',{'class':None})
        soup = BeautifulSoup(content, parseOnlyThese=daySummarylinks)
        
        for item in soup.contents:
                day = WeatherForecast.WeatherForecast()
                day.loadFrenchDay(item)
                list.extend(day.toHTML())
        
        #print u''.join(list)
	links = SoupStrainer('ul',{'id':'listeJoursLE'})
	soup= BeautifulSoup(content, parseOnlyThese=links)

	if(len(soup)==0):
		return

	for n in range(10):
		tendance = soup('li',{'class':'lijourle'+str(n)})
		#print tendance
		if(len(tendance) >0):
                        tend = WeatherForecast.WeatherForecast()
                        tend.loadFrenchTendance(tendance[0])
                        list.extend(tend.toHTML())
	list.append(u"</table>\n</div>")
	return list
	
def parseMeteoPageFrance(dico,content,tracking=""):
	domain = dico["domain"]
	suffix = dico["suffix"]	
	list = [u'']

	day=""
	indent="    "
	indent2=indent+indent

	cityInfosFilter = SoupStrainer('div',{'class':'choix'})
	otherSoup=BeautifulSoup(content,parseOnlyThese=cityInfosFilter)
	infosPage = otherSoup("p",text=True)
	#no post code on foreign cities
	cityName = infosPage[0]
	
	if len(infosPage) == 3 :
		lastUpdate = infosPage[2]
	else :
		#cityPostcode = infosPage[1]
		lastUpdate = infosPage[3]

	pageName = u"Pr&eacute;visions m&eacute;t&eacute;o pour "+cityName+" ".encode('utf-8')

	top = u"<html>\n<head>"+head+"<title>"+pageName+"</title>\n</head>\n<body>\n"
	

	list = [top]
	list.extend(getWeatherContentHTML_france(dico,content))

	list.append(foot+"\n<div>\n")
	list.append(u"<div class=\"nav\">Retourner &agrave <a href=\"/\">la liste des villes</a></div>\n")
	list.append(tracking)
	list.append("</body>\n</html>")
	return list        

def getSourceSentence(sourceUrl,pageName):
	return u"<div class=\"source\">Les informations sur cette page proviennent de la page de pr&eacute;visions de <a href=\""+sourceUrl+"\">M&eacute;t&eacute;o-France pour "+pageName+"</a>.</div>\n"


def generateIndex(infos,pagesAreFiles,tracking=""):
	list=[]
	list.append(u"<html>\n<head>")
	list.append(u"\t<title>M&eacute;t&eacute;o extraite des sites de M&eacute;t&eacute;o-France</title>")
	list.append(head)
	list.append(u"</head>\n<body><div class=\"content\"><p>Ce site web a &eacute;t&eacute; &eacute;crit pour pouvoir consulter les pr&eacute;visions de M&eacute;t&eacute;o-France sans crasher le navigateur web de l'iPhone.</p><div class=\"source\">Source des pr&eacute;visions : <a href=\"http://www.meteofrance.com/\">M&eacute;t&eacute;o-France</a></div>\n")
	list.append(u"<table>\n<thead><tr><th>Simple</th><th>Original</th></tr></thead>\n")

	for name,dico in infos.iteritems():
		pageAddress = name
		if pagesAreFiles :
			pageAddress=dico["file"]

		list.append(u"<tr>\n\t<td><a href=\""+pageAddress+"\">"+name+"</a></td>\n")
		list.append(u"\t<td><a href=\""+dico["domain"]+dico["suffix"]+"\">"+name+" chez M&eacute;t&eacute;o-France</a></td>\n</tr>\n")
			
	list.append(u"</table>\n"+foot+"\n</div>\n"+tracking+"\n<body></html>")
	return list


def getInfos():
	infos = {}
	f = open(namesFile)
	for line in f:
		l = line.split(',')
		infos[l[0]] = {"name":l[0],"domain":l[1],"suffix":l[2],"file":l[3]}
	    	#print "name : ",l[0]
	    	#print "domain: ",l[1]
	    	#print "suffix : ",l[2]
	    	#print "fileOut:,",l[3]	
	return infos


def getContent(opener,dico):
        response = opener.open("http://france.meteofrance.com/france/meteo?PREVISIONS_PORTLET.path=previsionsville/013130")
        result = opener.open(dico["domain"]+dico["suffix"]).read()
        return result

def writeFile(fileName,contentList):
	fileOut = open(base_dir+fileName,'w')
	outText = u''.join(contentList)
	text = outText.encode("iso-8859-1")
	fileOut.write(text)
	fileOut.close()

###############################
def main():
	import time
	#get the files informations
	infos = getInfos()
        cj = CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	if len(sys.argv)>1 and sys.argv[1] in infos:
		page = sys.argv[1]
		dico = infos[page]

		content= getContent(opener,dico)
                #content= ''.join(open('meteo.html','r').readlines())
		if("monde" in dico["domain"]):
			list = parseMeteoPage(dico,content)
		else:
			#france web page layout is very different
			list = parseMeteoPageFrance(dico,content)
		writeFile(dico["file"],list)
		print "did parse one of one page :",page	
		return
	else:
		print "Darn, asking for a nil or non existing page. Parsing all the pages every hours"

	indexStrings = generateIndex(infos,True)
	writeFile(listFile,indexStrings)
	i=0
	while 1:
		try:
			for name,dico in infos.iteritems():
				content= getContent(opener,dico)
				list = ""
				if("monde" in dico["domain"]):
					list = parseMeteoPage(dico,content)
				else:
					#france web page layout is very different
					list = parseMeteoPageFrance(dico,content)

				writeFile(dico["file"],list)
				print "did parse one of many page : ",name

		except Exception, e:
			print "Error while trying to parse/write the webpage : "
			print type(e)     # the exception instance
			print e.args      # arguments stored in .args
			print e
			
		print "## " + datetime.now().strftime(timeFormat) + " # Sleeping for an hour."
		time.sleep(3600)
		
		
		
		
if __name__== '__main__':
	main()
