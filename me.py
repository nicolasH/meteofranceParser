from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users


class UserSetupPage(webapp.RequestHandler):
	
	def get(self):
		self.response.headers['Content-Type'] = 'text/html'
		user = users.get_current_user()
		self.response.out.write("<html><head></head><body>")
		self.response.out.write("User info : ")
		self.response.out.write(user)
		self.response.out.write("</body></html>")
		return
		
application = webapp.WSGIApplication(
                                     [('/me',UserSetupPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()