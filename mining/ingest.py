#!/usr/bin/env python

"""
This script creates a normalized sqlite database of yelp data 
- Tables: businesses, users, reviews, categories, categories_businesses, categories_subcategories
- categories_subcategories captures the full category tree hierarchy  
- indices are created to speed up many useful queries
For eg:
This query outputs all the categories under "Restaurants" category
#> sqlite3 yelp.db "select C2.title from categories_subcategories as cs\
        , categories as C1, categories as C2 where cs.subcategory_id = C2.id\
        and cs.category_id=C1.id and C1.title='Restaurants'" 
"""

import sys
import sqlite3
from yelputils import yelprows


YELP_DB_SQL = [
"""create table if not exists businesses (
    id INTEGER not null,
    city TEXT,
    review_count INTEGER,
    name TEXT,
    open INTEGER,
    business_id TEXT not null,
    full_address BLOB,
    hours TEXT,
    state TEXT,
    longitude REAL,
    stars INTEGER,
    latitude REAL,
    attributes TEXT,
    categories TEXT,
    
    PRIMARY KEY (id ASC)
);
""",
"""
create table if not exists users (
    id INTEGER not null,
    name TEXT,
    yelping_since TEXT,
    review_count INTEGER,
    user_id TEXT NOT NULL,
    average_stars REAL,
    fans INTEGER,

    PRIMARY KEY (id ASC)
);
""",
"""
create table if not exists reviews (
    id INTEGER not null,
    review TEXT not null,
    business_id INTEGER not null,
    user_id INTEGER not null,
    review_id TEXT,
    stars INTEGER,
    date TEXT,
    funny INTEGER,
    useful INTEGER,
    cool INTEGER,

    PRIMARY KEY (id ASC),

    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (business_id) REFERENCES businesses(id)
);
""",
"""
create table if not exists categories (
    id INTEGER not null,
    title TEXT not null,
    alias TEXT,

    PRIMARY KEY (id ASC)
);
""",
"""
create table if not exists categories_businesses (
    
    category_id INTEGER not null,
    business_id INTEGER not null,

    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (business_id) REFERENCES businesses(id)
);
""",
"""
create table if not exists categories_subcategories (
    
    category_id INTEGER not null,
    subcategory_id INTEGER not null,

    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (subcategory_id) REFERENCES categories(id)
);
""",
"CREATE UNIQUE INDEX IF NOT EXISTS businesses_business_id_idx ON businesses (business_id)",
"CREATE UNIQUE INDEX IF NOT EXISTS users_user_id_idx ON users (user_id)",
"CREATE UNIQUE INDEX IF NOT EXISTS categories_title_idx ON categories (title)",
"CREATE INDEX IF NOT EXISTS reviews_businesses_business_id_idx ON reviews (business_id)",
"CREATE INDEX IF NOT EXISTS categories_businesses_category_id_idx ON categories_businesses (category_id)",
"CREATE INDEX IF NOT EXISTS categories_businesses_business_id_idx ON categories_businesses (business_id)",
"CREATE INDEX IF NOT EXISTS categories_subcategories_category_id_idx ON categories_subcategories (category_id)",
"CREATE INDEX IF NOT EXISTS categories_subcategories_subcategory_id_idx ON categories_subcategories (subcategory_id)",
]

SCHEMA = {
        "businesses":['city','review_count','name',
            'open','business_id','full_address','hours',
            'state','longitude','stars','latitude',
            'attributes','categories'],
        "users":['name','yelping_since',
            'review_count','user_id',
            'average_stars','fans'],
        "reviews":['review','business_id',
            'user_id','review_id','stars','date',
            'funny','useful','cool'],
        "categories": ['title', 'alias'],
        "categories_subcategories": ['category_id', 'subcategory_id']
}

YELP_DB = "yelp.db"
BUSINESS_DATA_PATH = "../../yelpdata/yelp_academic_dataset_business.json"
USER_DATA_PATH = "../../yelpdata/yelp_academic_dataset_user.json"
REVIEW_DATA_PATH = "../../yelpdata/yelp_academic_dataset_review.json"

def transform(data):
    if isinstance(data, dict) or isinstance(data, list):
        return repr(data)
    return data

class Ingestor(object):

    def __init__(self):
        self.conn = sqlite3.connect(YELP_DB)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        for table_sql in YELP_DB_SQL:
            try:
                self.cursor.execute(table_sql)
            except Exception, e:
                raise e
        self.conn.commit()

    def _insert(self, table, keys, values):

        try:
            stmt = "select max(id) from %s"%(table)
            self.cursor.execute(stmt)
            row = self.cursor.fetchone()
            max_id = -1
            if row[0]!=None:
                max_id = row[0]
            
            values.insert(0, 1+max_id)

            stmt = "insert into %s (%s) values (%s)"%(table, 'id,'+','.join(keys), ','.join(['?']*(1+len(keys))))
            self.cursor.execute(stmt, values)
            return 1+max_id
        except Exception,e:
            raise e

    def insert_category(self, title):
        table = 'categories'
        try:
            _id = self._insert(table, SCHEMA[table], [title, ''])
        except Exception, e:
            raise
        return _id

    def get_category_id(self, title):
        try:
            stmt = "select id from categories where title = ?"
            values = [title]
            self.cursor.execute(stmt, values)
            row = self.cursor.fetchone()
            return row[0]
        except Exception,e:
            return None

    def get_category_ids(self, category_titles):
        ret = []
        try:
            for title in category_titles:
                _id = self.get_category_id(title)
                if _id==None:
                    _id = self.insert_category(title)
                ret.append(_id)
        except Exception,e:
            raise e
        return ret

    def get_ids(self, table):
        self.cursor.execute("select id from %s"%table)
        rows = self.cursor.fetchall()
        ids = [row[0] for row in rows]
        return ids

    def insert_businesses(self, fpath=BUSINESS_DATA_PATH):
        IGNORE = ['id','neighborhoods', 'type']
        table = "businesses"
        try:
            for i, row in enumerate(yelprows(fpath)):
                keys = [k for k in SCHEMA[table] if k not in IGNORE ]
                values = [ transform(row[k]) for k in keys ]
                #stmt = "insert into businesses (" + ','.join(keys) + ") values (" +  ','.join(['?']*len(keys)) + ")"
                try:
                    _id = self._insert("businesses", keys, values)
                    categories = self.get_category_ids(row['categories'])
                    for category_id in categories:
                        self.cursor.execute("insert into categories_businesses values(?,?)", [category_id, _id])
                    self.conn.commit()
                except Exception, e:
                    print "Error, inserting same key mutiple times? -- %s"%str(e)
                if i%100 == 0:
                    print "%d finished"%i
        except Exception,e:
            raise
            print e

    def insert_users(self, fpath=USER_DATA_PATH):
        INCLUDE = ['name', 'yelping_since', 'review_count', 'user_id', 'average_stars', 'fans']
        for i,row in enumerate(yelprows(fpath)):
            try:
                keys = [k for k in row.keys() if k in INCLUDE ]
                values = [ transform(row[k]) for k in keys ]
                _id = self._insert("users", keys, values)
            except Exception,e:
                print e
            if i%1000==0:
                print "%d finished"%i
                self.conn.commit()

    def insert_reviews(self, fpath=REVIEW_DATA_PATH):
        EXCLUDE = ['type', 'votes']
        for i,row in enumerate(yelprows(fpath)):
            keys = [ k for k in row.keys() if k not in EXCLUDE ]
            values = []
           
            try:
                for k in keys:
                    if k == 'user_id':
                        values.append(self.get_id('users', k, row[k]))
                    elif k == 'business_id':
                        values.append(self.get_id('businesses', k ,row[k]))
                    else:
                        values.append(row[k])

                votes = row['votes']
                vkeys = votes.keys()
                vvalues = [votes[k] for k in vkeys]

                keys.extend(vkeys)
                values.extend(vvalues)
                
                keys = [ 'review' if k=='text' else k for k in keys ]
                
                _id = self._insert("reviews", keys, values)
            except Exception, e:
                pass

            if i%1000 == 0:
                self.conn.commit()
                print "%d finished"%i

    def create_category_tree(self):

        ids = self.get_ids('categories')
        for i,id1 in enumerate(ids):
            for id2 in ids:
                if id2 == id1:
                    continue

                b1 = set(self.get_businesses_for_category(id1))
                b2 = set(self.get_businesses_for_category(id2))
                
                if len(b1.intersection(b2)) == len(b2):
                    table = "categories_subcategories"
                    keys = SCHEMA[table]
                    values = [id1, id2]
                    stmt = "insert into %s (%s) values (%s)"%(table,  ','.join(keys), ','.join(['?']*len(keys)))
                    self.cursor.execute(stmt, values)
            if i%10==0:
                print i
                self.conn.commit()

    def get_businesses_for_category(self, category_id):

        stmt = "select business_id from categories_businesses where category_id = ?"
        values = [category_id]
        self.cursor.execute(stmt, values)
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]


    def get_id(self, table, key, value):
        stmt = "select id from %s where %s = ?"%(table, key)
        self.cursor.execute(stmt, [value])
        row = self.cursor.fetchone()
        return row[0]

    def close(self):
        self.conn.close()

if __name__=='__main__':

    ingestor = Ingestor()
    ingestor.create_tables()

    """
    Note: script may not be robust
    Do these steps carefully, one by one, I have not tried 
    running them all at once
    """
    #ingestor.insert_businesses()
    #ingestor.insert_users()

    """
    reviews table has a foreign key reference into users and businesses,
    so users and businesses have to ingested before reviews are ingested
    """
    #ingestor.insert_reviews()

    #ingestor.create_category_tree()
    ingestor.close()

