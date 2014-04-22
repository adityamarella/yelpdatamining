#!/usr/bin/env python

import collections
import json
import yelp
import os
from pprint import pprint

category_tree = []
with open('category.json') as f:
    category_tree = json.load(f)

category_tree = [yelp.category.Category(**c) for c in category_tree]

businesses = []

with open('../data/yelp_academic_dataset_business.json') as f:
    for line in f:
        businesses.append(yelp.business.Business(**json.loads(line)))

# pprint(category_tree)

# TODO: fix generator to properly flatten tree
def flatten_category_tree(tree):
    for cat in tree:
        if isinstance(cat, yelp.category.Category):
            yield cat
        flatten_category_tree(cat.category)

categories = [c for c in flatten_category_tree(category_tree)]

pprint(categories)
