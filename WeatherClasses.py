
imgDomainMobile = "http://mobile.meteofrance.com/"
class WeatherForecast(object):

    def __init__(self):
        self.forecast_name = None
        
        self.weather = None
        self.weather_img = None

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
        
    def loadFrenchPeriod(self, spoon):
        sp = spoon.contents
        self.forecast_name = sp[0].contents[0]
        
        self.weather = sp[1].img['title']
        self.weather_img = sp[1].img['src']
                
        # Contains non ascii char
        self.t_day = sp[2].contents[0]
        self.t_felt = sp[3].strong.contents[0] # ressentie
        
        # wind
        self.wind_dir_img= sp[4].span['class']
        self.wind_dir= sp[4].span['title']
        self.wind_speed = sp[4].strong.contents[0]
        # rafales
        self.wind_burst= sp[5].strong.contents[0]
        return self

    def loadFrenchDay(self,soup):
        ps = periodSoup
        
        self.period_name = ps('dt')[0].contents
        
        self.weather = ps('dd')[0]['title']
        self.weather_img = ps('dd')[0]['class']
        
        # Contains non ascii char
        self.t_min = ps('dd')[1].contents[0].contents[0]#min
        self.t_max = ps('dd')[1].contents[2].contents[0]#max

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
            self.details.append(WeatherForecast().loadFrenchPeriod(spoonful))

        return self

        
    def toHTML(self):
	list=[u'']
        
	weather = unicode.strip(self.weather)
	weather_img = unicode.strip(self.weather_img)
	
	wind_dir = unicode.strip(self.wind_dir)
	wind_dir_img = unicode.strip(self.wind_dir_img)
	wind_speed = unicode.strip(self.wind_speed)[3:]
        wind_busrt = self.wind_burst
	if wind_burst is None:
            wind_burst = '-'
        else:
            wind_burst = unicode.strip(wind_burst)

        classline=u''
        if(t_min is not None and t_max is not None):
            t_a = unicode.strip(t_min)
            t_b = unicode.strip(t_max)
            classLine="day"
        else:
            classLine="period"
            t_a = unicode.strip(t_day)
            t_b = unicode.strip(t_felt)

            
	#http://france.meteofrance.com/meteo/pictos/web/SITE/16/sud-sud-ouest.gif
	#http://france.meteofrance.com/meteo/pictos/web/SITE/30/32_c.gif
	# I prefer smaller icons
	weatherImg = self.weather_img.replace("CARTE/40","SITE/30")
	weatherImg = weatherImg.replace("SITE/40","SITE/30")
	weatherImg = weatherImg.replace("SITE/80","SITE/30")
	
	TD=u'</td>\n\t<td class="'+classline+'">'
	RTD=u'</td>\n\t<td class="'+classline+'" align="right">'
	
	list.append(u'<tr class="'+classline+'">\n\t')
	list.append(u'<td class="'+classline+'1">')
	list.append(self.forecast_name)
	list.append(TD+'<img src="'+imgDomainMobile+weather_img+'" width="30" height="30" ')
	list.append(u' alt="')
	list.append(weather)
	list.append(u'" title="')
	list.append(weather)
	list.append(u'" />' + RTD )
	list.append(t_a + ' | '+t_b)
	if(len(windImg)>0):
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
	return list

