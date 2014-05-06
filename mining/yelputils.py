import simplejson

def yelprows(fpath):
    fp = open(fpath)
    for line in fp:
        yield simplejson.loads(line.strip())
    fp.close()
