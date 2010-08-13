#!/usr/bin/python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup , SoupStrainer
import re
import urllib2
import codecs
import sys
import copy
import string

from datetime import datetime, date, time

###########

#constants
base_dir = "./"
namesFile = "./names.txt"
listFile = "index.html"

imgDomainMobile = "http://mobile.meteofrance.com/"
# header is geared toward iphone
head = u"""
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta name="viewport" content="width=350, user-scalable=yes">
	<link rel="stylesheet" href="css/weather.css" type="text/css" />
"""
foot =u"""
	<div class="footer">
		Les pr&eacute;visions m&eacute;t&eacute;o sont extraites du site de M&eacute;t&eacute;o-France. Elles sont reproduites en accord avec les informations pr&eacute;sentes sur la page concernant les <a href="http://france.meteofrance.com/france/accueil/informations_publiques">informations publiques</a>.
	</div>
"""
#timeFormat = "%A %d %B %Y - %H:%M:%S " 
timeFormat = "%Y/%m/%d &agrave; %H:%M:%S " 


###########
def parseAndDisplay(period,line,domain):
	list=[u'']
	weather = line.contents[2]
	###########################
	temperatures = weather.contents[1]
	weatherName = weather.img['alt']
	weatherImg = weather.img['src']
	###########################
	wind = line.contents[3]
	i = wind.contents[0]
	windSpeed = wind.contents[1]
	windDir = wind.img['title']
	windImg = wind.img['src']
	###########################
	rafales = line.contents[4]
	windMax=rafales.contents[0]
	###########################	
	weatherName	= unicode.strip(weatherName)
	weatherImg = unicode.strip(weatherImg)
	
	windD = unicode.strip(windDir)
	windI = unicode.strip(windImg)
	windS = unicode.strip(windSpeed)[3:]
	windM = unicode.strip(windMax)

	temp = temperatures
	temp = unicode.strip(temp)

	classLine="period"
	if temp.find("/")>0 :
		classLine="day"
		
	#http://france.meteofrance.com/meteo/pictos/web/SITE/16/sud-sud-ouest.gif
	#http://france.meteofrance.com/meteo/pictos/web/SITE/30/32_c.gif
	# I prefer smaller icons
	weatherImg = weatherImg.replace("CARTE/40","SITE/30")
	
	TD=u'</td>\n\t<td class="'+classLine+'">'
	RTD=u'</td>\n\t<td class="'+classLine+'" align="right">'
	
	list.append(u'<tr class="'+classLine+'">\n\t')
	list.append(u'<td class="'+classLine+'1">')
	list.append(period)
	list.append(TD+'<img src="'+imgDomainMobile+weatherImg+'" width="30" height="30" ')
	list.append(u' alt="')
	list.append(weatherName)
	list.append(u'" title="')
	list.append(weatherName)
	list.append(u'" />' + RTD )
	list.append(temp)
	list.append(TD + u'<img src="'+imgDomainMobile+windImg+'"')
	list.append(u' width="16" height="16" alt="')
	list.append(windDir)
	list.append(u'"title="')
	list.append(windDir)
	list.append(u'" />'+RTD)
	list.append(windSpeed)
	list.append(RTD)
	list.append(windM)
	list.append(u"</td>\n</tr>\n")
	return list


###########
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

	title = u"<html>\n<head>"+head+"<title>"+pageName+"</title>\n</head>\n<body>\n<div class=\"content\">\n"
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
				if day!=s[:n] :
					day=s[:n]
			else:#summary of that day or empty line?
				sDay=s
				weather = line.contents[2]
				if len(weather.contents)==0:
					#for the first line
					continue
				periodLine = parseAndDisplay("# "+sDay,line,domain)
				list.extend(periodLine)
				continue
		###########################
		## morning, afternoon etc ...
		period=line.contents[1]
		if len(period)==0:
			continue
		period=period.contents[0]
		############################
		## render
		periodLine = parseAndDisplay(period,line,domain)
		list.extend(periodLine)
	
	list.append(u"</table>\n"+foot+"\n<div>\n")
	list.append(u"<div clas=\"nav\">Retourner &agrave <a href=\"/\">la list des villes</a></div>\n")
	list.append(tracking)
	list.append("</body>\n</html>")
	return list


def displayInfos(period, weatherName , weatherImg, uv, temperatures, windDir , windImg, windSpeed,windMax):
	list=[u'']

	weatherName	= unicode.strip(weatherName)
	weatherImg = unicode.strip(weatherImg)
	
	windD = unicode.strip(windDir)
	windI = unicode.strip(windImg)
	windS = unicode.strip(windSpeed)[3:]
	windM = unicode.strip(windMax)

	temp = unicode.strip(temperatures)

	classLine="period"
	if temp.find("/")>0 :
		classLine="day"
		
	#http://france.meteofrance.com/meteo/pictos/web/SITE/16/sud-sud-ouest.gif
	#http://france.meteofrance.com/meteo/pictos/web/SITE/30/32_c.gif
	# I prefer smaller icons
	weatherImg = weatherImg.replace("CARTE/40","SITE/30")
	
	TD=u'</td>\n\t<td class="'+classLine+'">'
	RTD=u'</td>\n\t<td class="'+classLine+'" align="right">'
	
	list.append(u'<tr class="'+classLine+'">\n\t')
	list.append(u'<td class="'+classLine+'1">')
	list.append(period)
	list.append(TD+'<img src="'+imgDomainMobile+weatherImg+'" width="30" height="30" ')
	list.append(u' alt="')
	list.append(weatherName)
	list.append(u'" title="')
	list.append(weatherName)
	list.append(u'" />' + RTD )
	list.append(temp)
	list.append(TD + u'<img src="'+imgDomainMobile+windImg+'"')
	list.append(u' width="16" height="16" alt="')
	list.append(windDir)
	list.append(u'"title="')
	list.append(windDir)
	list.append(u'" />'+RTD)
	list.append(windSpeed)
	list.append(RTD)
	list.append(windM)
	list.append(u"</td>\n</tr>\n")
	return list
	
def parseMeteoPageFrance(dico,content,tracking=""):
	name = dico["name"]
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

	title = u"<html>\n<head>"+head+"<title>"+pageName+"</title>\n</head>\n<body>\n<div class=\"content\">\n"
	title +=u"<h1>"+pageName+"</h1>\n".encode('utf-8')
	title +=u"<h3>R&eacute;cuper&eacute; le "+datetime.now().strftime(timeFormat)+"</h3>\n"

	source = getSourceSentence(domain+suffix,cityName)

	list.append(title)
	list.append(source)
	list.append(u"<h3>"+lastUpdate+"</h3>")
	list.append(u"<table>")

	# current format in july-august / 2010
	# summaries in divs
	#				id -> jour0, jour1, jour2 
	#			 class -> "jour show_first" then "jour"
	# daily forecast in divs 
	#				id -> blockDetails0, blockDetails1, blockDetails2
	#			 class -> bloc_details
	# tendances in ul
	# 				id -> "suivants "
	#			 class -> listeJoursLE
	# 		class (li) -> lijourle0,lijourle1,lijourle2,lijourle3 ... 5
	
	#print "yaaaaaaa"
	# daily summaries
	for i in range(4):
		id = 'jour'+str(i)
		links = SoupStrainer('div',{'id':id})
		soup= BeautifulSoup(content, parseOnlyThese=links)
		#print "soup : " , len(soup)
		if(len(soup)==0):
			continue
		# Day + UV
		line = soup("strong")
		period = line[0].contents[0]
		periodUV = line[1].contents[0]
		# Temperature
		line = soup("em")
		periodTemp = line[0].contents[0]
		# Wind
		line = soup("p")
		periodWind = line[1].img['alt']
		periodWindSrc = line[1].img['src']
		periodWindSpeed = line[1].span.contents[0]
		line = soup("span")
		periodRafales = line[2].contents[0]
		#weather
		line = soup("div")
		periodWeather = line[2].img['alt']
		periodWeatherSrc = line[2].img['src']
		periodLine = displayInfos(period, periodWeather , periodWeatherSrc, periodUV, periodTemp, periodWind , periodWindSrc, periodWindSpeed, periodRafales)
		list.extend(periodLine)
		#print "# " , period
		#print " ->     : " , periodWeather , periodWeatherSrc
		#print " -> UV  : " , periodUV
		#print " -> °C  : " , periodTemp
		#print " -> wind: " , periodWind , periodWindSrc, periodWindSpeed
		#print " -> rafales: " , periodRafales

	for line in soup("strong"):
		period= ""
		print line
		# for the last line
		if len(line) < 4 :
			continue
		# for the daily summary	
		if(line.__dict__['attrs'] != None and len(line.__dict__['attrs'])>0 ):
			s = str(line.attrs[0][1]).decode('iso-8859-1')
			n= s.find(" ")
			if n>=0:
				if day!=s[:n] :
					day=s[:n]
			else:#summary of that day or empty line?
				sDay=s
				weather = line.contents[2]
				if len(weather.contents)==0:
					#for the first line
					continue
				periodLine = parseAndDisplay("# "+sDay,line,domain)
				list.extend(periodLine)
				continue
		###########################
		## morning, afternoon etc ...
		period=line.contents[1]
		if len(period)==0:
			continue
		period=period.contents[0]
		############################
		## render
		periodLine = parseAndDisplay(period,line,domain)
		list.extend(periodLine)
	
	list.append(u"</table>\n"+foot+"\n<div>\n")
	list.append(u"<div clas=\"nav\">Retourner &agrave <a href=\"/\">la list des villes</a></div>\n")
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


def getContent(dico):
	resp = urllib2.urlopen(dico["domain"]+dico["suffix"])
	return resp.read()


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
	
	if len(sys.argv)>1 and sys.argv[1] in infos:
		page = sys.argv[1]
		dico = infos[page]

		content= getContent(dico)
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
				content= getContent(dico)
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
