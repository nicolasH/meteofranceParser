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
head = """
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta name="viewport" content="width=350, user-scalable=yes">
	<link rel="stylesheet" href="weather.css" type="text/css" />
"""
	
timeFormat = "%A %d %B %Y - %H:%M:%S " 


###########
def parseAndDisplay(period,line,fi,domain):

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
	weatherName	= string.strip(weatherName)
	weatherImg = string.strip(weatherImg)
	
	windD = string.strip(windDir)
	windI = string.strip(windImg)
	windS = string.strip(windSpeed)[3:]
	windM = string.strip(windMax)

	temp = temperatures
	temp = string.strip(temp)

	classLine="period"
	if temp.find("/")>0 :
		classLine="day"
		
	#http://france.meteofrance.com/meteo/pictos/web/SITE/16/sud-sud-ouest.gif
	#http://france.meteofrance.com/meteo/pictos/web/SITE/30/32_c.gif
	TD='</td>\n\t<td class="'+classLine+'">'
	RTD='</td>\n\t<td class="'+classLine+'" align="right">'
	
	weatherImg = weatherImg.replace("CARTE/40","SITE/30")
	fi.write('<tr class="'+classLine+'">\n\t')
	fi.write('<td class="'+classLine+'1">')
	fi.write((u''+period).encode('iso-8859-1'))
	fi.write(TD+'<img src="'+domain+weatherImg+'"')
	fi.write((u'" alt="'+weatherName+'"').encode('iso-8859-1'))
	fi.write((u'" title="'+weatherName+'"').encode('iso-8859-1'))
	fi.write(' />')
	
	fi.write((u''+RTD + temp).encode('iso-8859-1'))
	fi.write(TD+'<img src="'+domain+windImg+'" alt="'+windDir+'"title="'+windDir+'" />')
	fi.write((u''+RTD+ windSpeed).encode('iso-8859-1'))
	fi.write((u''+RTD+ windM).encode('iso-8859-1'))
	fi.write("</td>\n</tr>\n")


###########
def getAndParse(name,domain,suffix,file):
	
	streamWriter = codecs.lookup('iso-8859-1')[-1]
	sys.stdout = streamWriter(sys.stdout)
	
	content=""	
	content = urllib2.urlopen(domain + suffix)
	
	links = SoupStrainer('table')
	soup= BeautifulSoup(content, parseOnlyThese=links)

	fi = open(base_dir+file,'w')
	s=""
	n=-1
	day=""
	indent="    "
	indent2=indent+indent
	
	cityName= name
	pageName = u"<title>M&eacute;t&eacute;o for "+cityName+"</title>".encode('utf-8')
	
	title = "<html><head>"+head+pageName+"</head><body>"
	title +=u"<h1>M&eacute;t&eacute;o for "+cityName+"</h1>".encode('utf-8')
	title +="<h3>Today is "+datetime.now().strftime(timeFormat)+"</h3>"
	source = getSourceSentence(domain+suffix,sourceName)
	fi.write(title)
	fi.write(source)
	fi.write("<table>")

	for line in soup("tr"):
		period=""
		# for the last line
		if len(line) < 4 :
			continue
		# for the daiy summary	
		if(line.__dict__['attrs'] != None and len(line.__dict__['attrs'])>0 ):
			s = str(line.attrs[0][1]).decode('iso-8859-1')
			n= s.find(" ")
			if n>=0:
				if day!=s[:n] :
					day=s[:n]
					#f.write("=====",day
			else:#summary of that day or empty line?
				sDay=s
				weather = line.contents[2]
				if len(weather.contents)==0:
					#for the first line
					continue
			
				parseAndDisplay("# "+sDay,line,fi,domain)		
				continue
		###########################
		## morning, afternoon etc ...
		period=line.contents[1]
		if len(period)==0:
			continue
		period=period.contents[0]
		############################
		## render
		parseAndDisplay(period,line,fi,domain)
	
	fi.write("</table></body></html>")
	fi.close()


def getSourceSentence(sourceUrl,sourceName):
	return "The informations on this page come from <a href=\""+sourceUrl+"\">"+sourceName+"</a>.<br/><br/>"



def printIndex(infos):
	
	f = open(base_dir+listFile,'w')
	f.write("<html>\n<head>")
	f.write("\t<title>Meteo parsed from the meteofrance sites</title>")
	f.write(head)
	f.write("</head>\n<body>Meteo parsed from <a href=\"http://www.meteofrance.com/\">"+sourceName+"</a><br/>\n")
	f.write("<table>\n<thead><tr><th>Simple page</th><th>Original</th></tr></thead>\n")

	for name,dico in infos.iteritems():
		f.write("<tr>\n\t<td><a href=\""+dico["file"]+"\">"+name+"</a></td>\n")
		f.write("\t<td><a href=\""+dico["domain"]+dico["suffix"]+"\">meteofrance for "+name+"</a></td>\n</tr>\n")
			
	f.write("</table>\n<body>\n</html>")
	f.close()

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
	    	
	#print infos
	printIndex(infos)
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
