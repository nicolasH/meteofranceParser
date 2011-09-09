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

#only france prevsions.
def displayInfos(period, weatherName , weatherImg, uv =u'', temperatures = u'', windDir = u'', windImg = u'', windSpeed = u'',windMax = u''):
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
	weatherImg = weatherImg.replace("SITE/40","SITE/30")
	weatherImg = weatherImg.replace("SITE/80","SITE/30")
	
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
	if(len(windImg)>0):
		#just a tendance
		list.append(TD + u'<img src="'+imgDomainMobile+windImg+'"')
		list.append(u' width="16" height="16" alt="')
		list.append(windDir)
		list.append(u'"title="')
		list.append(windDir)
		list.append(u'" />'+RTD)
		list.append(windSpeed)
		list.append(RTD)
		list.append(windM)
	else:
		list.append(TD+RTD)
		list.append(RTD)

	list.append(u"</td>\n</tr>\n")
	return list
	
#for the france part only.
def parsePeriod(soup):
	##Defining variables, so that I can use them later whether they have been filled or not
	period = periodWeather = periodWeatherSrc = periodUV = periodTemp = periodWind =  periodWindSrc =  periodWindSpeed = periodRafales = u''
	
	line = soup("strong")
	period = line[0].contents[0]
	periodUV= u''
	if len(line)>1 and len(line[1].contents)>0:
		periodUV=line[1].contents[0]
	# Temperature
	line = soup("em")
	periodTemp = line[0].contents[0]
	# Wind
	line = soup("p")
	if(len(line)>1):
		periodWind = line[1].img['alt']
		periodWindSrc = line[1].img['src']
		periodWindSpeed = line[1].span.contents[0]

	line = soup("span")
	if(len(line)>2):
		periodRafales = line[2].contents[0]
	#weather
	line = soup("div")
	if periodTemp.find("/")>0 :
		if(len(periodWind) >0):
			# a daily summary
			periodWeather = line[2].img['alt']
			periodWeatherSrc = line[2].img['src']
		else:
			#a fareway forecast
			periodWeather = line[0].img['alt']
			periodWeatherSrc = line[0].img['src']
	else:
		periodWeather = line[0].img['alt']
		periodWeatherSrc = line[0].img['src']
	
	periodLine = displayInfos(period, periodWeather , periodWeatherSrc, periodUV, periodTemp, periodWind , periodWindSrc, periodWindSpeed, periodRafales)
	
	return periodLine	

class PeriodWeather(object):
        def __init__(self, periodSoup):
                ps = periodSoup

                self.period_name = ps('dt')[0].contents

                self.weather = ps('dd')[0].img['alt']
                self.weather_img = ps('dd')[0].img['src']
                
                print self.weather, self.weather_img
                # Contains non ascii char
                self.t = ps('dd')[1].contents[0] 
                self.t_r = ps('dd')[2].strong.contents[0] # ressentie

                print self.t, self.t_r

                # wind
                self.wind_dir_img= ps('dd')[3].span['class']
                self.wind_dir= ps('dd')[3].span['title']
                self.wind_speed = ps('dd')[3].strong.contents[0]
                # rafales
                self.wind_burst= ps('dd')[4].strong.contents[0]
                print self.wind_dir_img, self.wind_dir, self.wind_speed, self.wind_burst

class DayWeather(object):
        def __init__(self, periodSoup):
                ps = periodSoup

                self.period_name = ps('dt')[0].contents

                self.weather = ps('dd')[0]['title']
                self.weather_img = ps('dd')[0]['class']
                
                
                print self.weather, self.weather_img
                # Contains non ascii char
                self.t_min = ps('dd')[1].contents[0].contents[0]
                self.t_max = ps('dd')[1].contents[2].contents[0]

                print self.t_min, self.t_max

                # wind
                self.wind_dir_img= ps('dd')[3].span['class']
                self.wind_dir= ps('dd')[3].span['title']
                self.wind_speed = ps('dd')[3].strong.contents[0]
                # rafales
                self.wind_burst= ps('dd')[4].strong.contents[0]
                print self.wind_dir_img, self.wind_dir, self.wind_speed, self.wind_burst
                self.details = []
                div = ps('dd')[5].contents[2].contents[0]
                for n in div:
                        print n.contents[0]('dd')
                        print type(n.contents[0])
#                periods = SoupStrainer('dl',{'class':''})
 #               gazpacho = BeautifulSoup(n, parseOnlyThese=periods)
  #              for item in gazpacho.contents:
   #                     print item
        



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

      	# current format in september 2011
	# summaries
        # ul: class=clearBoth
        #    li class = jour selected
        #       dl
        #         dt $day
        #         dd class="picTemps J_W1_0-N_0" title="$weather">Soleil</dd>
        #         -> day summary gets its weather picture from a sprite sheet via CSS
        #         dd - min | max
        #         dd - UV
        #         dd - vents
        #         dd - detail
        #       ...............
        #           dl
        #             dt $day
        #             dd img src="" title = "$weather"
        #             dd - temp
        #             dd - temp ressentie
        #             dd - UV
        #             dd - vents
	# daily summaries
        daySummarylinks = SoupStrainer('dl',{'class':None})
        soup = BeautifulSoup(content, parseOnlyThese=daySummarylinks)
        for item in soup.contents:
                day = DayWeather(item)
                print '##############################'
                print '%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%'
                periods = SoupStrainer('dl',{'class':''})
                gazpacho = BeautifulSoup(item.parent.contents[0], parseOnlyThese=periods)
                print '@@@@@@@@@@@@@@@@'
                print gazpacho
                
                
        return []
	for i in range(4):
		id = 'jour'+str(i)
		links = SoupStrainer('div',{'id':id})
		soup= BeautifulSoup(content, parseOnlyThese=links)

		if(len(soup)==0):
			continue

		periodLine = parsePeriod(soup)
		list.extend(periodLine)

		detailsId = 'blocDetails'+str(i)
		links = SoupStrainer('div',{'id':detailsId})
		soup= BeautifulSoup(content, parseOnlyThese=links)

		if(len(soup)==0):
			continue

		for echeance in soup('div',{'class':'echeance'}):
			periodLine = parsePeriod(echeance)			
			list.extend(periodLine)

	links = SoupStrainer('ul',{'id':'listeJoursLE'})
	soup= BeautifulSoup(content, parseOnlyThese=links)

	if(len(soup)==0):
		return

	for n in range(10):
		tendance = soup('li',{'class':'lijourle'+str(n)})
		#print tendance
		if(len(tendance) >0):
			tendanceLine = parsePeriod(tendance[0])
			list.extend(tendanceLine)

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

		#content= getContent(opener,dico)
                content= ''.join(open('meteo.html','r').readlines())
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
