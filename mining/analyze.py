#!/usr/bin/env python

import sqlite3
import simplejson
import operator
from yelputils import yelprows

fpath = "../../yelpdata/yelp_academic_dataset_business.json"

k = set([]) 

#print all the columns for business data
#Can we create a properly normalized database from this data?
for row in yelprows(fpath):
    k = k.union(row.keys())
print "Number of unique columns: %d"%len(k)
print repr(k)
print

#print unique categories
cats = {}
for row in yelprows(fpath):
    for item in row['categories']:
        cats[item] = cats.setdefault(item, 0) + 1

cats = sorted(cats.iteritems(), key=operator.itemgetter(1)) 
cats.reverse()

print "Num of unique categories: %d"%len(cats)
print cats[:10]
print

#print unique attributes
attrs = {}
for row in yelprows(fpath):
    for k,v in row['attributes'].iteritems():
        attrs.setdefault(str(type(v)), set([])).add(k)
print "Number of unique attrs: %d"%len(attrs)
print repr(attrs)
print

#print 'Good For' stats
nGoodFor = 0
nHours = 0
sattrs = ['Good For', 'Ambience']
N = [0]*len(sattrs)
per_attr_cnt = [{}, {}]
for row in yelprows(fpath):
    attrs = row['attributes']

    for i, k in enumerate(sattrs):
        gf = attrs.get(k, {})
        if len(gf) > 0:
            N[i] = N[i] + 1

        for k,v in gf.iteritems():
            if v == True:
                per_attr_cnt[i][k] = per_attr_cnt[i].setdefault(k, 0) + 1

for i,k in enumerate(sattrs):
    print "Number of businesses with '%s' info: %d"%(k, N[i])
    print per_attr_cnt[i]
    print

print

#print stats on how many businesses have hours info
