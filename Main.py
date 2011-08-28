# -*- coding: utf-8 -*-
import os
from Hi2Wp import Hi2Wp
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {'download_text': '', }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        
class Move(webapp.RequestHandler):
    def post(self):
        blog_id = self.request.get('blog_id')
        hi2wp = Hi2Wp(blog_id)
        hi2wp.get_entries()
        xml = hi2wp.get_xml()
        #xml = '<xml>'+blog_id+'</xml>'
        
        self.response.headers['Content-Disposition'] = "attachment; filename=hi2wp.xml"
        #template_values = {'download_text': '搬家完成，<a href="">点此下载文件</a>', }
        #path = os.path.join(os.path.dirname(__file__), 'index.html')
        #self.response.out.write(template.render(path, template_values))
        self.response.out.write(xml)
        
class Error(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'error.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/move', Move),
                                      ('/.*', Error)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
