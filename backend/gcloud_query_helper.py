#!/usr/bin/env python
#

import webapp2
from google.appengine.api import files
import logging
import MySQLdb
from google.appengine.ext import db
import os
import math
from datetime import datetime


# database name
_DB = 'yelp'
_INSTANCE_NAME = 'amarella-project-data:yelp'

class GCloudQueryHelper(object):

    def __init__(self):
        if (os.getenv('SERVER_SOFTWARE') and
            os.getenv('SERVER_SOFTWARE').startswith('Google App Engine/')):

            self.db = MySQLdb.connect(unix_socket='/cloudsql/' + _INSTANCE_NAME,
                    db=_DB, user='root')
        else:
            self.db = MySQLdb.connect(host='173.194.242.169',
                    unix_socket='/cloudsql/' + _INSTANCE_NAME,
                    db=_DB, user='root', passwd="")

        self.cursor = self.db.cursor()

    # Takes the database link and the query as input
    def run_query(self, query, bindings=[]):
        try:
            self.cursor.execute(query, bindings)
            return self.cursor.fetchall()
        except Exception, e:
            logging.info("query making failed %s"%str(e))
            return []

    def close(self):
        self.db.close()

