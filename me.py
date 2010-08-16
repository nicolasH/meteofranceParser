from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db

import cgi

class CityInfo(db.Model):
	cityKey = db.StringProperty()
	cityDomain = db.StringProperty()
	cityPage = db.StringProperty()


class UserPages(db.Model):
	userID = db.StringProperty()
	isPrivate = db.StringProperty()
	cityKey = db.StringProperty()

urlForm = """
	<form action="/me" method="post">
    	<div><input size="100" name="url" ></div>
        <div><input type="submit" value="Sign Guestbook" /></div>
	</form>
	"""

baseFrance = 'http://france.meteofrance.com/france/meteo?PREVISIONS_PORTLET.path=previsionsville/'
baseMonde = 'http://monde.meteofrance.com/monde/previsions?MONDE_PORTLET.path=previsionsvilleMonde/'

def urlCode(url):
	if baseFrance in url and len(url) < len(baseFrance) +7 :
		return [True,url[len(baseFrance):]]		
	if baseMonde in url and len(url) < len(baseMonde) +6:
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
+')want to get the weather forecast from : <pre>')
		url = cgi.escape(self.request.get('url'))
		res = urlCode(url)
		if res is None :
			self.response.out.write('unknown url')
		else :
			text = 'code '+ res[1]
			if res[0] : 
				text = 'a french city,' + text
			else :
				text =  ' a foreign city,' + text 
			self.response.out.write(text)
			
			
		self.response.out.write('</pre></body></html>')
	
application = webapp.WSGIApplication(
                                     [('/me',UserSetupPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()