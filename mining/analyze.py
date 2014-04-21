#!/usr/bin/env python

import sqlite3
import simplejson
import operator

def generate():
    fpath = "../../yelpdata/yelp_academic_dataset_business.json"
    fp = open(fpath)
    for line in fp:
        yield simplejson.loads(line.strip())
    fp.close()

k = set([]) 

#print all the columns for business data
#Can we create a properly normalized database from this data?
for row in generate():
    k = k.union(row.keys())
print "Columns: %s"%(repr(k))
print "####################"

#print unique categories
cats = {}
for row in generate():
    for item in row['categories']:
        cats[item] = cats.setdefault(item, 0) + 1

cats = sorted(cats.iteritems(), key=operator.itemgetter(1)) 
cats.reverse()

print "Num unique categories: %d"%len(cats)
print cats[:10]
print "####################"

#print unique attributes
attrs = {}
for row in generate():
    for k,v in row['attributes'].iteritems():
        attrs.setdefault(str(type(v)), set([])).add(k)
print "Unique attrs: %s"%(repr(attrs))
print "####################"
    
