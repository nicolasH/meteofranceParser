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
def renderHtml(period,temp,weatherName,weatherImg,windDir,windImg,windSpeed,windMax):
	temp = string.strip(temp)
	
	weatherName	= string.strip(weatherName)
	weatherImg = string.strip(weatherImg)
	
	windD = string.strip(windDir)
	windI = string.strip(windImg)
	windS = string.strip(windSpeed)[3:]
	windM = string.strip(windMax)
	
	classLine="period"
	if temp.find("/")>0 :
		classLine="day"
		
	#http://france.meteofrance.com/meteo/pictos/web/SITE/16/sud-sud-ouest.gif
	#http://france.meteofrance.com/meteo/pictos/web/SITE/30/32_c.gif
	TD='</td><td class="'+classLine+'">'
	RTD='</td><td class="'+classLine+'" align="right">'
	
	ft.write('<tr class="'+classLine+'">')
	ft.write('<td class="'+classLine+'1">')
	ft.write((u''+period).encode('iso-8859-1'))
	ft.write((u''+TD + weatherName).encode('iso-8859-1'))
#	f.write(TD+'<img src="'+domain+weatherImg+'">')
	ft.write((u''+RTD + temp).encode('iso-8859-1'))
	ft.write((u''+TD+ windDir).encode('iso-8859-1'))
#	f.write('<img src="'+domain+windImg+'" />')
	ft.write((u''+RTD+ windSpeed).encode('iso-8859-1'))
	ft.write((u''+RTD+ windM).encode('iso-8859-1'))
	ft.write("</td></tr>\n")

	weatherImg = weatherImg.replace("CARTE/40","SITE/30")
	fi.write('<tr class="'+classLine+'">')
	fi.write('<td class="'+classLine+'1">')
	fi.write((u''+period).encode('iso-8859-1'))
#	fi.write((u''+TD + weatherName).encode('iso-8859-1'))
	fi.write(TD+'<img src="'+domain+weatherImg+'"')
	fi.write((u'" alt="'+weatherName+'"').encode('iso-8859-1'))
       	fi.write((u'" title="'+weatherName+'"').encode('iso-8859-1'))
	fi.write(' />')
	
	fi.write((u''+RTD + temp).encode('iso-8859-1'))
#	fi.write((u''+TD+ windDir).encode('iso-8859-1'))
	fi.write(TD+'<img src="'+domain+windImg+'" alt="'+windDir+'"title="'+windDir+'" />')
	fi.write((u''+RTD+ windSpeed).encode('iso-8859-1'))
	fi.write((u''+RTD+ windM).encode('iso-8859-1'))
	fi.write("</td></tr>\n")

	
###########


domain = "http://france.meteofrance.com/"
streamWriter = codecs.lookup('iso-8859-1')[-1]
sys.stdout = streamWriter(sys.stdout)

content=""

#lines = open("meteo.html",'r').readlines()
#for line in lines:
#	content +=line.decode('iso-8859-1')
#f = open("meteo.html",'w')
ft = open("//srv/http/meteo/meteo_txt.html",'w')
fi = open("//srv/http/meteo/meteo_img.html",'w')

content = urllib2.urlopen("http://france.meteofrance.com/france/meteo?PREVISIONS_PORTLET.path=previsionsville/013130")

links = SoupStrainer('table')
soup= BeautifulSoup(content, parseOnlyThese=links)

s=""
n=-1
day=""
indent="    "
indent2=indent+indent

head = """
 <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
"""

head_T = """<meta name="viewport" content="width=600, user-scalable=yes">"""
head_I = """<meta name="viewport" content="width=350, user-scalable=yes">"""




css="""
<link rel="stylesheet" href="weather.css" type="text/css" />
"""

timeFormat = "%A %d %B %Y - %H:%M:%S " 

title_i = "<html><head>"+head+head_I
title_t = "<html><head>"+head+head_T

title = css+"</head><body>"

title +=u"<h1>M&eacute;t&eacute;o for PR&Eacute;VESSIN MO\xCBNS</h1>".encode('utf-8')

title +="<h3>Today is "+datetime.now().strftime(timeFormat)+"</h3>"

fi.write(title_i+title)
ft.write(title_t+title)

fi.write("<table>")
ft.write("<table>")
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
		###########################
			temperatures = weather.contents[1]
			weatherName = weather.img['alt']
			weatherImg = weather.img['src']
			#f.write("####",sDay
			#f.write(indent,"Temperatures : ",temperatures," temps ::",weatherName#," img:",weather.img['src']		
		###########################
			wind = line.contents[3]
			#if(hasattr(wind,'img') and wind.img !=None):
			i = wind.contents[0]
			windSpeed = wind.contents[1]
			windDir = wind.img['title']
			windImg = wind.img['src']
		###########################
			rafales = line.contents[4]
			rafaleSpeed=rafales.contents[0]
			#f.write(indent,"Vent ::["+windSpeed+"] max :["+rafaleSpeed+"]",windDir #,
			#f.write(indent,"Rafales ::",rafaleSpeed
			#f.write("<tr><td>&nbsp; </td></tr>")
			#render("#### "+sDay,temperatures,weatherName,weatherImg,windDir,windImg,windSpeed,rafaleSpeed)
			renderHtml("# "+sDay,temperatures,weatherName,weatherImg,windDir,windImg,windSpeed,rafaleSpeed)
			
			continue
	###########################
	## morning, afternoon etc ...
	period=line.contents[1]
	if len(period)==0:
		continue
	period=period.contents[0]
	#f.write(indent,period
	############################
	weather = line.contents[2]
	temperatures = weather.contents[1]
	weatherName = weather.img['alt']
	weatherImg = weather.img['src']
	#f.write(indent2,"Temperatures : ",temperatures," temps ::",weatherName#," img:",weather.img['src']		
	###########################
	wind = line.contents[3]
	i = wind.contents[0]
	windSpeed = wind.contents[1]
	windDir = wind.img['alt']
	windImg = wind.img['src']
	###########################
	rafales = line.contents[4]
	rafaleSpeed=rafales.contents[0]
	#f.write(indent2,windDir," vit: "+windSpeed,"max :",rafaleSpeed#,windDir #,
	############################
	## render
	#render(period,temperatures,weatherName,weatherImg,windDir,windImg,windSpeed,rafaleSpeed)
	renderHtml(period,temperatures,weatherName,weatherImg,windDir,windImg,windSpeed,rafaleSpeed)
	
	#f.write(indent2,"Vent ::",windSpeed," ",windDir #,
	#f.write(indent2,"Rafales ::",rafaleSpeed

fi.write("</table></body></html>")
ft.write("</table></body></html>")
fi.close()
ft.close()

