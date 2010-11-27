from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import memcache

import re
import cgi
import weather
import URLOpener

import main as main_

class CityInfo(db.Model):
	cityName = db.StringProperty()
	cityIsFrench = db.BooleanProperty()
	cityPage = db.StringProperty()


class MyCities(db.Model):
	userID = db.StringProperty()
	cityKey = db.StringProperty()

class UserAccount(db.Model):
	userNick = db.StringProperty()
	private = db.BooleanProperty()

scriptImport = """
<script src="/js/scripts.js"></script>
"""

##DEBUG
scriptBaseString="""
<textarea id="ajax" ></textarea>
"""

urlForm = """
	<div class="submitURL">
	<!--form class="submitCityURL" action="" method="post"-->
		<div class="submitTitle" >Ajoutez l'url d'une ville de <a href="http://france.meteofrance.com" >France</a> ou "<a href="http://monde.meteofrance.com/monde/previsions" >du Monde</a>":</div>
		<div class="urlField" ><input   id="urlField" name="url" ></div>
		<div class="urlSubmit" ><input type="button" value="Ajouter" onclick="asyncNewCity();" /></div>
	<!--/form-->
	</div>
	"""

baseFrance = 'http://france.meteofrance.com/france/meteo?PREVISIONS_PORTLET.path=previsionsville/'
baseMonde = 'http://monde.meteofrance.com/monde/previsions?MONDE_PORTLET.path=previsionsvilleMonde/'

domainFrance =  "http://france.meteofrance.com/"
domainMonde = "http://monde.meteofrance.com/"

suffixFrance = "france/meteo?PREVISIONS_PORTLET.path=previsionsville/"
suffixMonde = "monde/previsions?MONDE_PORTLET.path=previsionsvilleMonde/"

actionURL='/manage'
actionAdd = 'ajouter'
actionRemove = 'enlever'
whichID = 'which_city'

def urlCode(url):
	if url[0:len(baseFrance)] == baseFrance and len(url) < len(baseFrance) +7 :
		return [True,url[len(baseFrance):]]		
	if url[0:len(baseMonde)] == baseMonde and len(url) < len(baseMonde) +6:
		return [False, url[len(baseMonde):]]
	return None
	
def urlFromCode(isFrench,code):
	if isFrench:
		return baseFrance+code
	else:
		return baseMonde+code

def urlFromCityKey(cityKey):
	if cityKey[:2] == "fr" :
		return baseFrance+cityKey[3:]
	else:
		return baseMonde+cityKey[3:]

	
def cityCodeFromString(city_asked):
	"""
	expecting a string of the format fr_123456 or fr/123456
	will return a city_key which is of the form fr_123456 or mo_12345 
	"""
	regex = re.compile("([fr|mo]+)[\/|_](\d+)")
	rez = regex.search(city_asked)
	r = rez.groups()
	key=""
	if len(r)!=2 or (r[0]!="fr" and r[0]!="mo"):
		return ""
	#key=""
	if r[0]== "fr":
		key= r[0] +"_"+ r[1][0:6]
	if r[0]== "mo":
		key= r[0] +"_"+ r[1][0:5]
	return key

def thereURL(city):
	if city.cityIsFrench:
		return "there/fr/"+city.cityPage
	else:
		return "there/mo/"+city.cityPage

def cityLIcontent(city,form_id):
	city_key = city.key().name()
	key = city_key+"_"+form_id
	list =[]
	list.append("<a href='"+thereURL(city)+"'>")
	list.append(city.cityName)
	list.append("</a>")	
	if city.cityIsFrench :
		list.append(", france.")
	else:
		list.append(", monde.")
	list.append(" (voir <a href='"+urlFromCode(city.cityIsFrench,city.cityPage)+"'>original</a>) ")
	list.append("<input type='button' id='action_"+city_key+"' name='action' value='"+form_id+"' ") 
	list.append('onclick="asyncEdit(\''+city_key+'\',document.getElementById(\'action_'+city_key+'\').value);" ')
	list.append("/>")
	return u''.join(list)

def knownCitiesDIV(cities,excepted,title,form_id):
	list = ['<div class="cities">'+title+'\n\t\t<ul id="list_'+form_id+'" >\n']
	for city in cities:
		
		if excepted is not None and city.key().name() in excepted:
			continue
		list.append('\t\t\t<li id="item_'+city.key().name()+'" >')
		list.append(cityLIcontent(city,form_id))
		list.append("</li>\n")		
	list.append('</ul></div>')
	return list			


class SingleWeatherPage(webapp.RequestHandler):
	"""
	Handles the /there/* urls. Will fetch the forecast on the fly if url is possible and not already memcached.
	"""
	def get(self):
		self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
		
		city_asked = cgi.escape(self.request.path[7:])
		city_code = cityCodeFromString(city_asked)
		if(len(city_code)==0):
			self.response.out.write("ha HA! nice try.")
			return
		#self.response.out.write("city code = "+city_code)
		content = memcache.get(city_code)
		
		regexTitle=re.compile("<h1>([^<]*)</h1>.*")
		
		if(content is not None):
			rez = regexTitle.search(content)
			title = "<title>"+rez.groups()[0]+"</title>"
			self.response.out.write(u"<html><head>"+weather.head+title+"</head><body>")
			self.response.out.write(content)
			self.response.out.write(weather.foot)
			self.response.out.write(main_.extraCredits)
			self.response.out.write(main_.trackingScript)
			self.response.out.write(u'<body></html>')
			return

		dico = {}
		
		if city_code[0:3]== "fr_":
			dico["domain"] = domainFrance
			dico["suffix"] = suffixFrance + city_code[3:9]

		if city_code[0:3]== "mo_":
			dico["domain"] = domainMonde
			dico["suffix"] = suffixMonde + city_code[3:8]
		opener = URLOpener.URLOpener()
		fullPage = opener.open(dico["domain"]+dico["suffix"])
		list =[]
		if("PREVISIONS_PORTLET" in dico["suffix"]):
			#France web page layout is very different
			list = weather.getWeatherContentHTML_france(dico,fullPage.content)
		else:
			#Monde web page layout is very different
			list = weather.getWeatherContentHTML_monde(dico,fullPage.content)
		
		outText = u''.join(list)
		text = outText.encode("iso-8859-1")
		text2= db.Text(text, encoding="UTF-8")
		
		rez = regexTitle.search(text2)
		title = "<title>"+rez.groups()[0]+"</title>"
		
		memcache.set(city_code,text2,3600)
		
		self.response.out.write(u"<html><head>"+weather.head+title+"</head><body>")
		self.response.out.write(text2)		
		self.response.out.write(weather.foot)
		if users.get_current_user() is not None:
			self.response.out.write('<a href="/me">Aller a vos pages</a>')
		else:
			self.response.out.write('Vous pouvez <a href="/me">creer un compte</a> et y enregistrer vos villes favorites.')
		self.response.out.write(main_.extraCredits)
		self.response.out.write(main_.trackingScript)
			
		self.response.out.write(u'<body></html>')
		return

class UserWeatherPagesManager(webapp.RequestHandler):

	def get(self):
		userID = users.get_current_user().user_id()
		self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
		action = cgi.escape(self.request.get('action'))

		city_asked = cgi.escape(self.request.get('which_city'))
		city_code = ''
		possibleID=""
		if(city_asked != None):
			key = cityCodeFromString(city_asked)
			if(None == key or len(key)==0):
				self.response.out.write("ha HA! nice try.")
				return

		self.response.out.write("city code = "+key)
		if action == actionAdd :
			city = CityInfo.get_by_key_name(key)
		
			link = MyCities(key_name=key+"_"+userID)
			link.cityKey = key
			link.userID = userID
			link.put()
		if action == actionRemove :
			link = MyCities.get_by_key_name(key+"_"+userID)
			link.delete()
		return		
			
class UserSetupPage(webapp.RequestHandler):
	"""
	The "home" page for each user.
	"""
	def get(self):
		#self.response.headers['Content-Type'] = 'text/html; charset=iso-8859-1'
		self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
		user = users.get_current_user()
		userID = user.user_id()
		account = UserAccount()
		account.userNick = user.nickname()
		account.private= False
		account.get_or_insert(key_name=user.user_id())

		self.response.out.write("<html><head>"+weather.head+scriptImport+"</head><body>")
		##DEBUG
		self.response.out.write(scriptBaseString)
		self.response.out.write("<div class=\"me\">")
		self.response.out.write("<h1>Welcome "+user.nickname()+"</h1>")

		self.response.out.write(urlForm)

		myCities = db.GqlQuery("SELECT * FROM MyCities WHERE userID = :1",userID)
		#NOT OPTIMAL
		personnalCities = []
		exceptedKeys=[]
		for mine in myCities:
			#Never removing a city, are we ?
			personnalCities.append(CityInfo.get_by_key_name(mine.cityKey))
			exceptedKeys.append(mine.cityKey)
				
		divTitle =""
		if(len(personnalCities)>0):
			divTitle= u'Vos Villes (<a href="/mine">Pr&eacute;visions</a>) :'
		else:
			divTitle=u'Vous devriez ajouter des villes'

		list = knownCitiesDIV(personnalCities,None,divTitle,"enlever")
		self.response.out.write(u''.join(list))
		
		allCities = db.GqlQuery("SELECT * FROM CityInfo LIMIT 50")
		list = knownCitiesDIV(allCities,exceptedKeys,"Toute les autres villes :","ajouter")
		self.response.out.write(u''.join(list))
		self.response.out.write('</div>')
		self.response.out.write('<body></html>')
		
		return
		
	def post(self):
		self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
		userID = users.get_current_user().user_id()
		
		url = cgi.escape(self.request.get('url'))
		res = urlCode(url)
		if res is None :
			self.response.out.write('unknown page : '+url)
			return
		url = res[1]
		cityName = u''
		if res[0] : 
			url = baseFrance + url
		else :
			url = baseMonde + url
			
		text = "Adding this : "
		opener = URLOpener.URLOpener()
		result = opener.open(url)
		key = ''
		if res[0]:
			cityName = weather.getCityNameFrance(result.content)
			text += "[french, "+cityName+", "+res[1]+"]"
			key='fr_'+res[1]
		else:
			cityName = weather.getCityNameMonde(result.content)
			text += "[world, "+cityName+", "+res[1]+"]"
			key='mo_'+res[1]
			
		#self.response.out.write(text)
		
		cityName = u'' + cityName
		
		city = CityInfo(key_name=key)
		city.cityIsFrench = res[0]
		city.cityPage = res[1]
		city.cityName = cityName
		city.put()
			
		link = MyCities(key_name=key+"_"+userID)
		link.cityKey = key
		link.userID = userID
		link.put()
		
		self.response.out.write('{"id":"item_'+key+'","content":"'+cityLIcontent(city,"enlever").replace('"','\\"')+'"}')

class UserWeatherPages(webapp.RequestHandler):
	"""
	The forecast for each city the user has saved the url.
	-> this might time out if there are too many cities as app engine has a 30 seconds request limit.
	"""
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		userID = users.get_current_user().user_id()

		self.response.out.write(u"<html><head>"+weather.head+"</head><body>")
		self.response.out.write(u'<div class="content"><h1> Vos Pr&eacute;visions:</h1></div>')

		myCities = db.GqlQuery("SELECT * FROM MyCities WHERE userID = :1",userID)

		opener = URLOpener.URLOpener()
			
		for mine in myCities:
			content = memcache.get(mine.cityKey)
			if content is not None:
				self.response.out.write(content)
			else:
				cityUrl = urlFromCityKey(mine.cityKey)
				fullPage = opener.open(url=cityUrl)#(dico["domain"]+dico["suffix"]))
				dico={}
				list=[]
				if mine.cityKey[:2]=="fr":
					dico["domain"] = domainFrance
					dico["suffix"] = suffixFrance + mine.cityKey[3:]
					list = weather.getWeatherContentHTML_france(dico,fullPage.content)
				if mine.cityKey[:2]=="mo":
					dico["domain"] = domainMonde
					dico["suffix"] = suffixMonde + mine.cityKey[3:]
					list = weather.getWeatherContentHTML_monde(dico,fullPage.content)
	
				outText = u''.join(list)
				text = outText.encode("iso-8859-1")
				text2= db.Text(text, encoding="UTF-8")
				memcache.set(mine.cityKey,text2,3600)
				self.response.out.write(text2)
		self.response.out.write(weather.foot)
		self.response.out.write(main_.extraCredits)
		self.response.out.write(main_.trackingScript)
		self.response.out.write(u'<body></html>')
		return

			
		return
	
	
application = webapp.WSGIApplication(
                                     [('/me',UserSetupPage),
                                     ('/manage',UserWeatherPagesManager),
                                     ('/mine',UserWeatherPages),
                                     ('/there/.*',SingleWeatherPage)],
                                     debug=True)

def main():
	opener=URLOpener.URLOpener()
	run_wsgi_app(application)

if __name__ == "__main__":
    main()