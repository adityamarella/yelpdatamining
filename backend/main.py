#!/usr/bin/env python
#

import urllib
import logging
import datetime
import webapp2
import gviz_api
from webapp2_extras import jinja2
from webapp2_extras import json
from django.utils import simplejson

from gcloud_query_helper import GCloudQueryHelper

# BaseHandler subclasses RequestHandler so that we can use jinja
class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(app=self.app)

    def render_response(self, _template, context):
        values = {'url_for': self.uri_for}
        logging.info(context)
        values.update(context)
        self.response.headers['Content-Type'] = 'text/html'

        try: 
            rv = self.jinja2.render_template(_template, **values)
            self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
            self.response.write(rv)
        except TemplateNotFound:
            self.abort(404)

# Class MainHandler now subclasses BaseHandler instead of webapp2
class MainHandler(BaseHandler):

    def __init__(self, *args, **kwargs):
        BaseHandler.__init__(self, *args, **kwargs)
        self.query_helper = GCloudQueryHelper()
        
    # This method should return the html to be displayed
    def get(self):
       
        try: 
            mode = self.request.get("mode", None)
            resp_type = self.request.get("format", None)

            if mode==None or resp_type==None:
                raise NameError("input format error")
             
            category = int(self.request.get("category", -1))

            projection = ['id', 'term', 'freq']

            stmt = "select %s from %s\
                    where category_id=%%s\
                    order by freq desc limit 100"%(','.join(projection), mode)
            rows = self.query_helper.run_query(stmt, (category))

            data_table = gviz_api.DataTable(projection)
            data_table.LoadData(rows)
            resp = data_table.ToJSonResponse(columns_order=tuple(projection)) 

            headers = self.write_response(resp, resp_type, 200)
        except NameError,e:
            logging.error(e)
            headers = self.write_response("Error: %s"%str(e), resp_type, 400)
        except Exception,e:
            logging.error(e)
            headers = self.write_response("Error: %s"%str(e), resp_type, 500)

    def write_response(self, resp, resp_type, status):
        headers = {}
        if resp_type == "json":
            headers["Content-Type"] = "application/json"
        else:
            headers["Content-Type"] = "text/html"

        if status == 200:
            headers["Status"] = "200 OK"
        elif status == 400:
            headers["Status"] = "400 Bad Request"
        else:
            headers["Status"] = "500 Internal Server Error"
        
        for k,v in headers.iteritems():
            self.response.headers[k] = v
        self.response.out.write("%s"%resp)


app = webapp2.WSGIApplication([('/.*', MainHandler)], debug=True)
