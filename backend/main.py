#!/usr/bin/env python
#

import urllib
import logging
import datetime
import webapp2
import gviz_api
import random
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

    def adjectivenoun(self, category):
        projection = ['id', 'term', 'freq']

        if category == -1:
            stmt = "select id, term, sum(freq) as s from adjectivenoun\
                    order by s desc group by term limit 100"
            rows = self.query_helper.run_query(stmt)
        else:
            stmt = "select %s from adjectivenoun\
                    where category_id=%%s\
                     order by freq desc limit 100"%(','.join(projection))
            rows = self.query_helper.run_query(stmt, (category))

        description = {
                "id": ("number", 'id'),
                "term": ("string", "term"),
                "freq": ("number", "freq")}
        data = []
        for row in rows:
            data.append(dict(zip(projection, row)))

        random.shuffle(data)

        data_table = gviz_api.DataTable(description)
        data_table.LoadData(data)
        return data_table.ToJSon(columns_order=tuple(projection)) 

    def ldatopics(self, category, table="ldatopics"):  
        projection = ["topic_id","term", "freq"]

        stmt = "select %s from %s\
                where category_id=%%s"%(','.join(projection), table)
        rows = self.query_helper.run_query(stmt, (category))

        description = {
                "topic_id": ("number", 'topic_id'),
                "term": ("string", "term"),
                "freq": ("number", "freq")}

        data = []
        for row in rows:
            data.append(dict(zip(projection, row)))
        
        random.shuffle(data)

        data_table = gviz_api.DataTable(description)
        data_table.LoadData(data)
        return data_table.ToJSon(columns_order=tuple(projection)) 

    def get_static_data(self, mode):
        fpath = "data/%s.json"%mode
        return open(fpath).read()
        
    # This method should return the html to be displayed
    def get(self):
       
        try: 
            mode = self.request.get("mode", None)
            resp_type = self.request.get("format", None)

            if mode==None or resp_type==None:
                raise NameError("input format error")
             
            category = int(self.request.get("category", -1))

            if category==-1:
                resp = self.get_static_data(mode)
            else:
                resp = ""
                if mode=="adjectivenoun":
                    resp = self.adjectivenoun(category)
                elif mode=="topics":
                    resp = self.ldatopics(category)
                elif mode=="cluster":
                    resp = self.ldatopics(category, table='yelpcluster')

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
            headers["Content-Type"] = "text/plain"

        if status == 200:
            headers["Status"] = "200 OK"
        elif status == 400:
            headers["Status"] = "400 Bad Request"
        else:
            headers["Status"] = "500 Internal Server Error"

        headers['Access-Control-Allow-Origin'] = '*'
        
        for k,v in headers.iteritems():
            self.response.headers[k] = v
        self.response.out.write("%s"%resp)


app = webapp2.WSGIApplication([('/.*', MainHandler)], debug=True)
