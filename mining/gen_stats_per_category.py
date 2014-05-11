#!/usr/bin/env python

from query_helper import QueryHelper
from adjectivenoun import AdjectiveNoun


if __name__=='__main__':

    yelp_db_path = "yelp.db"
    query_helper = QueryHelper(yelp_db_path)

    adjnoun = AdjectiveNoun(query_helper)
    adjnoun.process()

    query_helper.close()

