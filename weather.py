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
sourceName = "the Meteo-France website"
# header is geared toward iphone
head = u"""
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta name="viewport" content="width=350, user-scalable=yes">
	<link rel="stylesheet" href="weather.css" type="text/css" />
"""
	
timeFormat = "%A %d %B %Y - %H:%M:%S " 


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
def getAndParse(name,domain,suffix,file):
	
	list = [u'']
	content=""	
	content = urllib2.urlopen(domain + suffix)

	links = SoupStrainer('table')
	soup= BeautifulSoup(content, parseOnlyThese=links)

	s=""
	n=-1
	day=""
	indent="    "
	indent2=indent+indent
	
	cityName= name
	pageName = u"<title>M&eacute;t&eacute;o for "+cityName+"</title>".encode('utf-8')
	
	title = u"<html><head>"+head+pageName+"</head><body>"
	title +=u"<h1>M&eacute;t&eacute;o for "+cityName+"</h1>".encode('utf-8')
	title +=u"<h3>Today is "+datetime.now().strftime(timeFormat)+"</h3>"
	source = getSourceSentence(domain+suffix,sourceName)
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

	
	list.append(u"</table></body></html>")
	fileOut = open(base_dir+file,'w')
	outText = u''.join(list)
	text = outText.encode("iso-8859-1")
	fileOut.write(text)
	fileOut.close()


def getSourceSentence(sourceUrl,sourceName):
	return u"The informations on this page come from <a href=\""+sourceUrl+"\">"+sourceName+"</a>.<br/><br/>"



def generateHtmlIndex(infos):
	list=[]
	list.append(u"<html>\n<head>")
	list.append(u"\t<title>Meteo parsed from the meteofrance sites</title>")
	list.append(head)
	list.append(u"</head>\n<body>Meteo parsed from <a href=\"http://www.meteofrance.com/\">"+sourceName+"</a><br/>\n")
	list.append(u"<table>\n<thead><tr><th>Simple page</th><th>Original</th></tr></thead>\n")

	for name,dico in infos.iteritems():
		list.append(u"<tr>\n\t<td><a href=\""+dico["file"]+"\">"+name+"</a></td>\n")
		list.append(u"\t<td><a href=\""+dico["domain"]+dico["suffix"]+"\">meteofrance for "+name+"</a></td>\n</tr>\n")
			
	list.append(u"</table>\n<body>\n</html>")
	return list

####################
def main():
	import time
	#get the files informations
	infos = {}
	with open(namesFile) as f:
	    for line in f:
	    	l = line.split(',')
	    	infos[l[0]] = {"name":l[0],"domain":l[1],"suffix":l[2],"file":l[3]}
	    	#print "name : ",l[0]
	    	#print "domain: ",l[1]
	    	#print "suffix : ",l[2]
	    	#print "fileOut:,",l[3]	
	    	
	if len(sys.argv)>1 and sys.argv[1] in infos:
		page = sys.argv[1]
		dico = infos[page]
		getAndParse(dico["name"],dico["domain"],dico["suffix"],dico["file"])
		print "did parse ",page	
		return
	else:
		print "Darn, asking for a nil or non existing page. Parsing all the pages every hours"


	indexStrings = generateHtmlIndex(infos)
	fileOut = open(base_dir+listFile,'w')
	fileOut.write(''.join(indexStrings))
	fileOut.close()

	while 1:
		try:
			for name,dico in infos.iteritems():
				getAndParse(dico["name"],dico["domain"],dico["suffix"],dico["file"])
				print "did parse ",name
				
		except Exception as e:
			print "Error while trying to parse/write the webpage : "
			print type(e)     # the exception instance
			print e.args      # arguments stored in .args
			print e
			
		print "## " + datetime.now().strftime(timeFormat) + " # Sleeping for an hour."
		time.sleep(3600)
		
		
		
		
if __name__== '__main__':
	main()
