from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.api import urlfetch

import cgi
import weather

class CityInfo(db.Model):
	cityName = db.StringProperty()
	cityIsFrench = db.BooleanProperty()
	cityPage = db.StringProperty()


class UserPages(db.Model):
	userID = db.StringProperty()
	isPrivate = db.StringProperty()
	cityKey = db.ReferenceProperty()

urlForm = """
	<form action="/me" method="post">
    	<div><input size="130" name="url" ></div>
        <div><input type="submit" value="Add City" /></div>
	</form>
	"""

baseFrance = 'http://france.meteofrance.com/france/meteo?PREVISIONS_PORTLET.path=previsionsville/'
baseMonde = 'http://monde.meteofrance.com/monde/previsions?MONDE_PORTLET.path=previsionsvilleMonde/'

def urlCode(url):
	if url[0:len(baseFrance)] == baseFrance and len(url) < len(baseFrance) +7 :
		return [True,url[len(baseFrance):]]		
	if url[0:len(baseMonde)] == baseMonde and len(url) < len(baseMonde) +6:
		return [False, url[len(baseMonde):]]
	return None
	
class UserSetupPage(webapp.RequestHandler):
	
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		self.response.out.write("<html><head></head><body>")
		self.response.out.write("User info : ")
		self.response.out.write(user)
		self.response.out.write(" id: " + user.user_id())
		self.response.out.write(urlForm)
		self.response.out.write("</body></html>")
		return
		
	def post(self):
		self.response.out.write('<html><body>You ('+users.get_current_user().user_id()
+') want to get the weather forecast from : <br/>')
		url = cgi.escape(self.request.get('url'))
		res = urlCode(url)
		if res is None :
			self.response.out.write('unknown url')
		else :
			text = 'code '+ res[1]
			url = res[1]
			cityName = u''
			if res[0] : 
				text = 'a french city,' + text
				url = baseFrance + url
			else :
				text =  ' a foreign city,' + text 
				url = baseMonde + url
				
			self.response.out.write(text)
		#
			text = "Gonna insert the following object "
			result = urlfetch.fetch(url)
			key = ''
			if res[0]:
				cityName = weather.getCityNameFrance(result.content)
				text += "[french, "+cityName+", "+res[1]+"]"
				key='fr_'+res[1]
			else:
				cityName = weather.getCityNameMonde(result.content)
				text += "[foreign, "+cityName+", "+res[1]+"]"
				key='mo_'+res[1]
			
			self.response.out.write(text)
			
			#cn = cityName.encode("iso-8859-1")
			#cn = db.Text(cityName, encoding="iso-8859-1")

			
			city = CityInfo(key_name=key)
			city.cityIsFrench = res[0]
			city.cityPage = res[1]
			city.cityName = cityName
			city.put()
						 		
		self.response.out.write('</body></html>')
	
application = webapp.WSGIApplication(
                                     [('/me',UserSetupPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()