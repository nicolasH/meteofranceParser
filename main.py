from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext import db
from datetime import datetime, date, time,timedelta

import weather

trackingScript = u"""
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-3650019-3']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(ga);
  })();

</script>"""

class CityStore(db.Model):
	cityKey = db.StringProperty()
	content = db.TextProperty()
	dateFetch = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
    def get(self):
        
        self.response.headers['Content-Type'] = 'text/html'
        infos = weather.getInfos()
        if len(self.request.path)>1 :
        	page = self.request.path[1:]
        	if page in infos :
				lastPages = db.GqlQuery("SELECT * FROM CityStore WHERE cityKey = :1",page)
				lastPages.fetch(1)
				if lastPages.count() > 0 and (datetime.now() - lastPages[0].dateFetch)< timedelta(minutes=59):
					self.response.out.write(lastPages[0].content)
					return
				dico = infos[page]
				fullPage = result = urlfetch.fetch(url=(dico["domain"]+dico["suffix"]))
				list =""
				if("monde" in dico["domain"]):
					#france web page layout is very different
					list = weather.parseMeteoPage(dico,fullPage.content,trackingScript)
				else:
					#france web page layout is very different
					list = weather.parseMeteoPageFrance(dico,fullPage.content,trackingScript)

				#list = weather.parseMeteoPage(dico,fullPage.content,trackingScript)
				outText = u''.join(list)
				text = outText.encode("iso-8859-1")
				cityS = CityStore(key_name=page)
				cityS.content = db.Text(text, encoding="utf-8")
				cityS.cityKey = page
				self.response.out.write(text)
				cityS.put()
				return
        
        indexStrings= weather.generateIndex(infos,False,trackingScript)
        self.response.out.write(u''.join(indexStrings))
        
		
application = webapp.WSGIApplication(
                                     [('/.*', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()