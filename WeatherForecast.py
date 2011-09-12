# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup , SoupStrainer
import string
import codecs

import re
import urllib2
import urllib
import codecs
import sys
import copy
import string
imgDomainMobile = "http://mobile.meteofrance.com/"
class WeatherForecast(object):

    def __init__(self):
        self.forecast_name = None
        
        self.weather = None
        self.weather_img = None

        self.UV = None

        self.t_min = None
        self.t_max = None

        self.t_day = None
        self.t_felt = None
        
        # wind
        self.wind_dir_img = None
        self.wind_dir = None
        self.wind_speed = None
        # rafales
        self.wind_burst = None
        
        self.details = None
        
    def loadFrenchTendance(self, soup):

	line = soup("strong")
	# Day
        self.forecast_name = line[0].contents[0]#date
	self.UV = u''
	if len(line)>1 and len(line[1].contents)>0:
		self.UV=line[1].contents[0]
	# Weather
	line = soup("div")
        #a fareway forecast
        self.weather = line[0].img['alt']
        self.weather_img = line[0].img['src']

	# Temperature
	line = soup("em")
        t = line[0].contents[0].__str__('utf-8')
        t = unicode(t,'iso-8859-1')#min
	self.t_min = t.split('/')[0]
	self.t_max = t.split('/')[1]

        # Wind: no wind
        

##################################


    def loadFrenchPeriod(self, spoon):
        sp = spoon.contents
        self.forecast_name = sp[0].contents[0]

        self.weather = sp[1].img['title']
        self.weather_img = sp[1].img['src']
                
        # Contains non ascii char
        self.t_day = sp[2].contents[0].__str__('utf-8')
        self.t_day = unicode(self.t_day,'iso-8859-1')

        self.t_felt = sp[3].strong.contents[0].__str__('utf-8')
        self.t_felt = unicode(self.t_felt,'iso-8859-1') # ressentie
        
        # wind
        self.wind_dir_img= sp[4].span['class']
        self.wind_dir= sp[4].span['title']
        self.wind_speed = sp[4].strong.contents[0]
        # rafales
        self.wind_burst= sp[5].strong.contents[0]


    def loadFrenchDay(self,soup):
        ps = soup
        
        self.forecast_name = ps('dt')[0].contents[0]
        
        self.weather = ps('dd')[0]['title']
        self.weather_img = ps('dd')[0]['class']
        
        # Contains non ascii char
        self.t_min = ps('dd')[1].contents[0].contents[0].__str__('utf-8')
        self.t_min = unicode(self.t_min,'iso-8859-1')#min
        self.t_max = ps('dd')[1].contents[2].contents[0].__str__('utf-8')
        self.t_max = unicode(self.t_max,'iso-8859-1')#max

        # wind
        self.wind_dir_img= ps('dd')[3].span['class']
        self.wind_dir= ps('dd')[3].span['title']
        self.wind_speed = ps('dd')[3].strong.contents[0]
                # rafales
        self.wind_burst= ps('dd')[4].strong.contents[0]
        
        self.details = []
        ul = ps('dd')[5].contents[2]
        content = str(ul.contents[0])
        periodSummarylinks = SoupStrainer('dl',{'class':''})
        soup = BeautifulSoup(content, parseOnlyThese=periodSummarylinks)
        for spoonful in soup:
            p_forecast = WeatherForecast()
            self.details.append(p_forecast)
            p_forecast.loadFrenchPeriod(spoonful)

        
    def toHTML(self):
	list=[u'']
        fc = self.forecast_name.__str__('utf-8')
        fc = unicode(fc,'iso-8859-1')

        weather = self.weather
        weather = weather.encode('utf-8')
        weather = unicode(weather,'iso-8859-1')

        #print weather, type(weather)
	weather_img = unicode.strip(self.weather_img)
        wind_dir = wind_dir_img = wind_speed = u''
	if self.wind_dir is not None:
            wind_dir = unicode.strip(self.wind_dir)
            wind_dir_img = unicode.strip(self.wind_dir_img)
            wind_speed = unicode.strip(self.wind_speed)
        else:
            wind_dir = '&emdash;'
            wind_dir_img = ''
            wind_speed = '&emdash;'
        
        wind_burst = self.wind_burst

	if wind_burst is None:
            wind_burst = '&emdash;'
        else:
            wind_burst = unicode.strip(wind_burst)

        classline=u''
        t_sep = u'/'
        if(self.t_min is not None and self.t_max is not None):
            classline="day"
            t_a = unicode.strip(self.t_min)
            t_b = unicode.strip(self.t_max)
            t_sep = u' / '
        else:
            classline="period"
            t_a = unicode.strip(self.t_day)
            t_b = unicode.strip(self.t_felt)
            t_sep = u' ~ '

        #wind
	#http://france.meteofrance.com/meteo/pictos/web/SITE/16/sud-sud-ouest.gif
	#weather
        #http://france.meteofrance.com/meteo/pictos/web/SITE/30/32_c.gif
        
            
        #from meteofrance
        #http://france.meteofrance.com/meteo/pictos/web/SITE/40/0_a.gif
        #from my page - wrong
        #http://mobile.meteofrance.com/meteo_files/0_a_002.gif
	# I prefer smaller icons
        print self.weather_img
        #http://france.meteofrance.com/meteo/pictos/web/SITE/40/7_a.gif
	weatherImg = self.weather_img.replace("CARTE/40","SITE/30")
	weatherImg = weatherImg.replace("SITE/40","SITE/30")
	weatherImg = weatherImg.replace("SITE/80/","SITE/30/")
	print weatherImg
	TD=u'</td>\n\t<td class="'+classline+'">'
	RTD=u'</td>\n\t<td class="'+classline+'" align="right">'
	
	list.append(u'<tr class="'+classline+'">\n\t')
	list.append(u'<td class="'+classline+'1">')
	list.append(u''+fc)
	list.append(TD+'<img src="'+imgDomainMobile+weatherImg+'" width="30" height="30" ')
	list.append(u' alt="')
	list.append(weather)
	list.append(u'" title="')
	list.append(weather)
	list.append(u'" />' + RTD )
	list.append(t_a + t_sep + t_b)
	if(len(wind_dir_img)>0):
		list.append(TD + u'<img src="'+imgDomainMobile+wind_dir_img+'"')
		list.append(u' width="16" height="16" alt="')
		list.append(wind_dir)
		list.append(u'"title="')
		list.append(wind_dir)
		list.append(u'" />'+RTD)
		list.append(wind_speed)
		list.append(RTD)
		list.append(wind_burst)
	else:
		#just a tendance
		list.append(TD+RTD)
		list.append(RTD)

	list.append(u"</td>\n</tr>\n")

        if self.details is not None:
            for detail in self.details:
                list.extend(detail.toHTML())
	return list

