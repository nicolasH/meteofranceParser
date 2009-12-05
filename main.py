from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
import weather

class MainPage(webapp.RequestHandler):
    def get(self):
        
        self.response.headers['Content-Type'] = 'text/html'
        infos = weather.getInfos()
        if len(self.request.path)>1 :
        	page = self.request.path[1:]
        	if page in infos :
				dico = infos[page]
				fullPage = result = urlfetch.fetch(url=(dico["domain"]+dico["suffix"]))
				list = weather.parseMeteoPage(dico,fullPage.content)
				outText = u''.join(list)
				text = outText.encode("iso-8859-1")
				self.response.out.write(text)
				return
        
        indexStrings= weather.generateIndex(infos,False)
        self.response.out.write(u''.join(indexStrings))
        
		
application = webapp.WSGIApplication(
                                     [('/.*', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()