from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import urlfetch

import re
import cgi
import weather

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

scriptString = """
	<script language="javascript">
	function asyncEdit(cityID,action){
		var xhr; 
    	try {  
    		xhr = new ActiveXObject('Msxml2.XMLHTTP');
    	}catch (e) {
        	try {   
        		xhr = new ActiveXObject('Microsoft.XMLHTTP');
        	}catch (e2) {
				try {  
					xhr = new XMLHttpRequest();
          		}catch (e3) {  xhr = false;   }
        	}
     	}
 
    	xhr.onreadystatechange  = function(){ 
			if(xhr.readyState  == 4){
        		if(xhr.status  == 200) 
        	         document.getElementById('ajax').value="Received:"  + xhr.responseText; 
        	    else 
        	         document.getElementById('ajax').value="Error code " + xhr.status;
        	 }
    	}; 

   		xhr.open("GET", "/manage?which_city="+cityID+"&action="+action,  true); 
   		xhr.send(null);
	}
</script>
<input id="ajax" type="text" value="response should appear here" size="100" />
"""


urlForm = """
	<div class="submitURL">
	<form class="submitCityURL" action="/me" method="post">
		<div class="submitTitle" >Ajoutez l'url d'une ville :</div>
		<div class="urlField" ><input  size="110" name="url" ></div>
		<div class="urlSubmit" ><input type="submit" value="Ajouter" /></div>
	</form>
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
		

def knownCitiesDIV(cities,title,formID):
	list = ['<div class="cities">'+title+'<ul>\n']
	for city in cities:
		key = city.key().name()+"_"+formID
		cityKey = city.key().name()
		list.append('<li>')
		list.append(city.cityName)
		
		if city.cityIsFrench :
			list.append(", france.")
		else:
			list.append(", monde.")
		list.append(' (voir <a href="'+urlFromCode(city.cityIsFrench,city.cityPage)+'">original</a>) ')
		list.append('<input type="button" name="action" value="'+formID+'" onclick="asyncEdit(\''+cityKey+'\',\''+formID+'\');" /></form>\n')
		list.append('</li>\n')
		
	list.append('</ul></div>')
	return list			
	
class UserWeatherPagesManager(webapp.RequestHandler):

	def get(self):
		userID = users.get_current_user().user_id()
		self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
		action = cgi.escape(self.request.get('action'))

		city_asked = cgi.escape(self.request.get('which_city'))
		city_code = ''
		possibleID=""
		regex = re.compile("([fr_|mo_]+)(\d+)")
		rez = regex.search(city_asked)
		r = rez.groups() 
		if len(r)!=2 or (r[0]!="fr_" and r[0]!="mo_"):
			self.response.out.write("ha HA! nice try.")
			return
		#key=""
		if r[0]== "fr_":
			key= r[0] + r[1][0:6]
		if r[0]== "mo_":
			key= r[0] + r[1][0:5]
		
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
	
	def get(self):
		#self.response.headers['Content-Type'] = 'text/html; charset=iso-8859-1'
		self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
		user = users.get_current_user()
		userID = user.user_id()
		account = UserAccount()
		account.userNick = user.nickname()
		account.private= False
		account.get_or_insert(key_name=user.user_id())

		self.response.out.write("<html><head>"+weather.head+"</head><body>")
		
		self.response.out.write(scriptString)
		self.response.out.write("<div class=\"me\">")
		self.response.out.write("<h1>Welcome "+user.nickname()+"</h1>")

		self.response.out.write(urlForm)

		myCities = db.GqlQuery("SELECT * FROM MyCities WHERE userID = :1",userID)
		#NOT OPTIMAL
		personnalCities = []
		for mine in myCities:
			#Never removing a city, are we ?
			personnalCities.append(CityInfo.get_by_key_name(mine.cityKey))
				
		list = knownCitiesDIV(personnalCities,"Mes villes :","enlever")
		self.response.out.write(u''.join(list))
		
		allCities = db.GqlQuery("SELECT * FROM CityInfo LIMIT 50")
		list = knownCitiesDIV(allCities,"Toute les autres villes :","ajouter")
		self.response.out.write(u''.join(list))
		self.response.out.write('</div>')
		self.response.out.write('<body></html>')
			
		return
		
	def post(self):
		userID = users.get_current_user().user_id()
		self.response.headers['Content-Type'] = 'text/html; charset=UTF-8'
		self.response.out.write('<html><head>'+weather.head+'</head><body><div class="me">You ('+userID +') want to get the weather forecast from : <br/>')
		url = cgi.escape(self.request.get('url'))
		res = urlCode(url)
		if res is None :
			self.response.out.write('unknown page')
		else :
			text = 'code '+ res[1]
			url = res[1]
			cityName = u''
			if res[0] : 
				text = 'a french city,' + text
				url = baseFrance + url
			else :
				text =  ' a world city,' + text 
				url = baseMonde + url
				
			self.response.out.write(text)
			#
			text = "<br/>Gonna insert the following object "
			result = urlfetch.fetch(url)
			key = ''
			if res[0]:
				cityName = weather.getCityNameFrance(result.content)
				text += "[french, "+cityName+", "+res[1]+"]"
				key='fr_'+res[1]
			else:
				cityName = weather.getCityNameMonde(result.content)
				text += "[world, "+cityName+", "+res[1]+"]"
				key='mo_'+res[1]
			
			self.response.out.write(text)
			
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
		myCities = db.GqlQuery("SELECT * FROM CityInfo LIMIT 50")
		list = knownCitiesDIV(myCities,"Known Cities","rien")
		self.response.out.write(u''.join(list))
		
		self.response.out.write('</div></body></html>')

class UserWeatherPages(webapp.RequestHandler):
	
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		userID = users.get_current_user().user_id()

		self.response.out.write(u"<html><head>"+weather.head+"</head><body>")
		self.response.out.write(u'<div class="content"><h1> Mes Pr&eacute;visions:</h1></div>')

		myCities = db.GqlQuery("SELECT * FROM MyCities WHERE userID = :1",userID)
		#NOT OPTIMAL
		personnalCities = []
		for mine in myCities:
			#Never removing a city, are we ?
			personnalCities.append(CityInfo.get_by_key_name(mine.cityKey))
		
		dicos = []
		for city in personnalCities:
			dico = {}
			if city.cityIsFrench :
				dico["domain"] = domainFrance
				dico["suffix"] = suffixFrance + city.cityPage
			else:
				dico["domain"] = domainMonde
				dico["suffix"] = suffixMonde+ city.cityPage
			dicos.append(dico)
		
		for dico in dicos:
			fullPage = urlfetch.fetch(url=(dico["domain"]+dico["suffix"]))
			if("PREVISIONS_PORTLET" in dico["suffix"]):
				#France web page layout is very different
				list = weather.getWeatherContentHTML_france(dico,fullPage.content)
				outText = u''.join(list)
				text = outText.encode("iso-8859-1")
				text2= db.Text(text, encoding="UTF-8")
				self.response.out.write(text2)
			else:
				#Monde web page layout is very different
				list = weather.getWeatherContentHTML_monde(dico,fullPage.content)
				outText = u''.join(list)
				text = outText.encode("iso-8859-1")
				text2= db.Text(text, encoding="UTF-8")
				self.response.out.write(text2)
				
		self.response.out.write(weather.foot)
		self.response.out.write(u'<body></html>')
			
		return
	
application = webapp.WSGIApplication(
                                     [('/me',UserSetupPage),
                                     ('/manage',UserWeatherPagesManager),
                                     ('/mine',UserWeatherPages)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()