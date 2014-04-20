#!/usr/bin/env python
#

import urllib
import logging
import datetime
import webapp2
from webapp2_extras import jinja2
from webapp2_extras import json
from django.utils import simplejson

DATE_FORMAT = "%Y-%m-%d"

BUSINESS_INFO_ATTRS = ['name', 'full_address', 'type', 'stars']

# BaseHandler subclasses RequestHandler so that we can use jinja
class BaseHandler(webapp2.RequestHandler):

    @webapp2.cached_property
    def jinja2(self):
        # Returns a Jinja2 renderer cached in the app registry.
        return jinja2.get_jinja2(app=self.app)

        # This will call self.response.write using the specified template and context.
        # The first argument should be a string naming the template file to be used. 
        # The second argument should be a pointer to an array of context variables
        #  that can be used for substitutions within the template
    def render_response(self, _template, context):
        # Renders a template and writes the result to the response.
        values = {'url_for': self.uri_for}
        logging.info(context)
        values.update(context)
        self.response.headers['Content-Type'] = 'text/html'

        # Renders a template and writes the result to the response.
        try: 
            rv = self.jinja2.render_template(_template, **values)
            self.response.headers['Content-Type'] = 'text/html; charset=utf-8'
            self.response.write(rv)
        except TemplateNotFound:
            self.abort(404)

# Class MainHandler now subclasses BaseHandler instead of webapp2
class MainHandler(BaseHandler):
        
        # This method should return the html to be displayed
    def get(self):
       
        mode = self.request.get("mode", "gettoken")
        resp_type = self.request.get("type", "html")
       
        try:
            if mode == "gettoken":
                token = self.request.get("tk", "")
                token_source = self.request.get("tsrc", "adjnoun")
                logging.info("params: mode: %s, tk: %s, tsrc: %s"%(mode, token, token_source))
                data = self.get_business_ids(token, token_source)
                data = self.get_business_info(data)

            elif mode == "getbusinessinfo":
                bids = self.request.get("bids", None)
                logging.info("params: mode: %s, bids: %s"%(mode, bids))
                data = self.get_business_info(bids.split(","))

            status = "200 OK"

        except Exception, e:
            data = "Server Error: %s"%str(e)
            status = "501 Not Implemented"
            raise e

        finally:
            if resp_type == "json":
                self.response.headers["Content-Type"] = "application/json"
                self.response.headers["Status"] = status
                self.response.out.write("%s"%(json.encode(data, 'utf-8')))
            else:
                context = {"data": data}
                self.render_response('index.html', context)

    def get_business_info(self, business_ids):
        """ collect data from the server. """

        try:
            data = getattr(self, "business_info")
        except AttributeError:
            data = None

        if not data:
            fpath = "data/business.json"
            try:
                fp = open(fpath)
                data = {}
                for line in fp:
                    d=simplejson.loads(line.strip())
                    data[d["business_id"]] = d
                fp.close()
                setattr(self, "business_info", data)
            except IOError:
                logging.info("failed to load file")

        ret = {}
        for bid in business_ids:
            v = data.get(bid, {})
            ret[bid] = { a:b for a,b in v.iteritems() if a in BUSINESS_INFO_ATTRS}

        return ret

    def get_business_ids(self, token, token_source):
        try:
            data = getattr(self, "self.%s"%token_source)
        except AttributeError:
            data = None

        if not data:
            fpath = "data/adjnoun.json"
            try:
                fp = open(fpath)
                data = eval(fp.read())
                setattr(self, "self.%s"%token_source, data)
                fp.close()
            except IOError:
                logging.info("failed to load file")
        
        return data[token]

    def convert_html(self, data):
        pass

app = webapp2.WSGIApplication([('/.*', MainHandler)], debug=True)
