#!/usr/bin/python
# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup , SoupStrainer
import re
import urllib2
import codecs
import sys
import string

from datetime import datetime, date, time

###########

#constants
base_dir = "./"
namesFile = "./names.txt"
listFile = "index.html"

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
	list.append(TD+'<img src="'+domain+weatherImg+'"')
	list.append(u" alt=")
	list.append(weatherName)
	list.append(u'" title="')
	list.append(weatherName)
	list.append(u'" />' + RTD )
	list.append(temp)
	list.append(TD+'<img src="'+domain+windImg+'" alt="')
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
def parseMeteoPage(dico,content):
	name = dico["name"]
	domain = dico["domain"]
	suffix = dico["suffix"]	
	list = [u'']

	links = SoupStrainer('table')
	soup= BeautifulSoup(content, parseOnlyThese=links)

	s=""
	n=-1
	day=""
	indent="    "
	indent2=indent+indent
	
	cityName= name
	
	pageName = u"M&eacute;t&eacute;o pour "+cityName+"".encode('utf-8')
	
	title = u"<html><head>"+head+"<title>"+pageName+"</title>\n</head>\n<body>\n<div class=\"content\">\n"
	title +=u"<h1>"+pageName+"</h1>\n".encode('utf-8')
	title +=u"<h3>R&eacute;cuper&eacute; le "+datetime.now().strftime(timeFormat)+"</h3>\n"
	source = getSourceSentence(domain+suffix,cityName)
	list.append(title)
	list.append(source)
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
					#list.append("=====",day
			else:#summary of that day or empty line?
				sDay=s
				weather = line.contents[2]
				if len(weather.contents)==0:
					#for the first line
					continue
			
				periodLine = parseAndDisplay("# "+sDay,line,domain)
				list.extend(periodLine)
				#repr(list)
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
	
	list.append(u"</table>\n"+foot+"\n<div></body>\n</html>")
	return list

def getSourceSentence(sourceUrl,pageName):
	return u"<div class=\"source\">Les informations sur cette page proviennent de la page de pr&eacute;visions de <a href=\""+sourceUrl+"\">M&eacute;t&eacute;o-France pour "+pageName+"</a>.</div>\n"



def generateIndex(infos,pagesAreFiles):
	list=[]
	list.append(u"<html>\n<head>")
	list.append(u"\t<title>M&eacute;t&eacute;o extraite des sites de M&eacute;t&eacute;o-France</title>")
	list.append(head)
	list.append(u"</head>\n<body><div class=\"content\"><div class=\"source\">Source : <a href=\"http://www.meteofrance.com/\">M&eacute;t&eacute;o-France</a></div>\n")
	list.append(u"<table>\n<thead><tr><th>Simple</th><th>Original</th></tr></thead>\n")

	for name,dico in infos.iteritems():
		pageAddress = name
		if pagesAreFiles :
			pageAddress=dico["file"]

		list.append(u"<tr>\n\t<td><a href=\""+pageAddress+"\">"+name+"</a></td>\n")
		list.append(u"\t<td><a href=\""+dico["domain"]+dico["suffix"]+"\">"+name+" chez M&eacute;t&eacute;o-France</a></td>\n</tr>\n")
			
	list.append(u"</table>\n"+foot+"\n</div>\n<body></html>")
	return list

####################
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

def writeFile(fileName,contentList):
	fileOut = open(base_dir+fileName,'w')
	outText = u''.join(contentList)
	text = outText.encode("iso-8859-1")
	fileOut.write(text)
	fileOut.close()
	
def main():
	import time
	#get the files informations
	infos = getInfos()
	
	if len(sys.argv)>1 and sys.argv[1] in infos:
		page = sys.argv[1]
		dico = infos[page]

		content = urllib2.urlopen(dico["domain"]+dico["suffix"])

		list = parseMeteoPage(dico,content)
		writeFile(dico["file"],list)
		print "did parse one of one page :",page	
		return
	else:
		print "Darn, asking for a nil or non existing page. Parsing all the pages every hours"

	indexStrings = generateIndex(infos,True)
	writeFile(listFile,indexStrings)

	while 1:
		try:
			for name,dico in infos.iteritems():

				content = urllib2.urlopen(dico["domain"]+dico["suffix"])

				list = parseMeteoPage(dico,content)

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
