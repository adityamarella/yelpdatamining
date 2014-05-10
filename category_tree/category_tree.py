#!/usr/bin/env python

from __future__ import print_function
from collections import deque
import json
import yelp
import os
from pprint import pprint
import sys


def search_category_tree(root, alias=None, title=None):
    if alias is None and title is None:
        return None

    if alias is not None and title is not None:
        raise RuntimeError("Cannot search for both title and alias")

    categoryStack = [category for category in root.category]
    try:
        top = categoryStack.pop()
    except IndexError:
        top = None
    while top is not None:
        if alias is not None and top.alias == alias:
            return top
        elif title is not None and top.title == title:
            return top
        categoryStack.extend([category for category in top.category])
        try:
            top = categoryStack.pop()
        except IndexError:
            top = None

def enumerate_category_tree(root):
    categories = [("Category", "Parent", "Business Count")]
    categoryQueue = deque([(root, None)])

    while len(categoryQueue) != 0:
        node, parent_title = categoryQueue.popleft()
        categories.append((node.title, parent_title, node.business_count))
        [categoryQueue.append((category, node.title)) for category in node.category]

    return categories


class CategoryEncoder(json.JSONEncoder):
    """A JSONEncoder for CategoryTree.
    """
    def default(self, obj):
        if isinstance(obj, yelp.category.Category):
            return {'alias': obj.alias,
                    'title': obj.title,
                    'business_count': obj.business_count,
                    'category': obj.category
                   }
        # Let the base class default method raise the TypeError
        return super().default(self, obj)


def normalize_category_title(category_title):
    if category_title == "Beauty & Spas":
        category_title = "Beauty and Spas"
    elif category_title == "Books, Mags, Music & Video":
        category_title = "Books, Mags, Music and Video"
    elif category_title == "Chocolatiers & Shops":
        category_title = "Chocolatiers and Shops"
    elif category_title == "Divorce & Family Law":
        category_title = "Divorce and Family Law"
    elif category_title == "Flowers":
        category_title = "Flowers & Gifts"
    elif category_title == "Hair Stylists":
        category_title = "Hair Salons"
    elif category_title == "Health & Medical":
        category_title = "Health and Medical"
    elif category_title == "Herbs & Spices":
        category_title = "Herbs and Spices"
    elif category_title == "Hot Tub & Pool":
        category_title = "Hot Tub and Pool"
    elif category_title == "Junk Removal & Hauling":
        category_title = "Junk Removal and Hauling"
    elif category_title == "Men's Hair Salons":
        category_title = "Hair Salons"
    elif category_title == "Obstetricians & Gynecologists":
        category_title = "Obstetricians and Gynecologists"
    elif category_title == "Videos & Video Game Rental":
        category_title = "Videos and Video Game Rental"
    elif category_title == "Vocational & Technical School":
        category_title = "Vocational and Technical School"
    # The following category titles from the academic dataset are ignored:
    #     Anesthesiologists
    #     Auction Houses
    #     Barre Classes
    #     Bartenders
    #     Beer Hall
    #     Blow Dry/Out Services
    #     Boat Dealers
    #     Boot Camps
    #     Boxing
    #     Bubble Tea
    #     Business Law
    #     CSA
    #     Cafeteria
    #     Cantonese
    #     Cocktail Bars
    #     Colombian
    #     Comfort Food
    #     Commercial Real Estate
    #     Courthouses
    #     Cultural Center
    #     Cupcakes
    #     Damage Restoration
    #     Diagnostic Imaging
    #     Diagnostic Services
    #     Door Sales/Installation
    #     Event Photography
    #     Fences & Gates
    #     Food Court
    #     Food Trucks
    #     Formal Wear
    #     Gelato
    #     Gift Shops
    #     Gold Buyers
    #     Golf Equipment
    #     Gymnastics
    #     Hats
    #     Hearing Aid Providers
    #     Home Window Tinting
    #     Hot Air Balloons
    #     Hypnosis/Hypnotherapy
    #     Irrigation
    #     Jewelry Repair
    #     Laboratory Testing
    #     Laser Tag
    #     Lebanese
    #     Matchmakers
    #     Medical Supplies
    #     Mobile Phone Repair
    #     Party Bus Rentals
    #     Party Equipment Rentals
    #     Payroll Services
    #     Permanent Makeup
    #     Personal Assistants
    #     Pharmacy
    #     Piano Bars
    #     Pita
    #     Pretzels
    #     RV Parks
    #     Race Tracks
    #     Registration Services
    #     Resorts
    #     Rugs
    #     Session Photography
    #     Shared Office Spaces
    #     Shaved Ice
    #     Spray Tanning
    #     Talent Agencies
    #     Ticket Sales
    #     Uniforms
    #     Urologists
    #     Utilities
    #     Wheel & Rim Repair
    #     Wigs
    #     Yelp Events

    return category_title


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--categories', type=argparse.FileType('r'), required=True,
                        help='a file containing a JSON object of categories')
    parser.add_argument('businesses', type=argparse.FileType('r'),
                        help='a file containing the a list of business JSON objects')
    parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
                        help='write output to file')
    args = parser.parse_args()

    # 1. create category tree
    root = yelp.category.Category(alias="root",
                                  title="Root",
                                  category=json.load(args.categories))

    # 2. count each business in each category and sub-category
    businesses = []
    for line in args.businesses:
        businesses.append(yelp.business.Business(**json.loads(line)))

    for business in businesses:
        for category_title in business.categories:
            # some category titles need to be cleaned and normalized
            category_title = normalize_category_title(category_title)

            try:
                category = search_category_tree(root, title=category_title)
                category.businesses.add(business)
            except AttributeError:
                # ignore all unknown categories
                # (see list in `normalize_category_title`)
                pass

    # 3. output category tree with business counts as JSON
    # Each row in the data table describes one node (a rectangle in the graph). Each node (except the root node) has one or more parent nodes. Each node is sized and colored according to its values relative to the other nodes currently shown.
    # The data table should have four columns in the following format:
    #     Column 0 - [string] An ID for this node. It can be any valid JavaScript string, including spaces, and any length that a string can hold. This value is displayed as the node header.
    #     Column 1 - [string] - The ID of the parent node. If this is a root node, leave this blank. Only one root is allowed per treemap.
    #     Column 2 - [number] - The size of the node. Any positive value is allowed. This value determines the size of the node, computed relative to all other nodes currently shown. For non-leaf nodes, this value is ignored and calculated from the size of all its children.
    #     Column 3 - [optional, number] - An optional value used to calculate a color for this node. Any value, positive or negative, is allowed. The color value is first recomputed on a scale from minColorValue to maxColorValue, and then the node is assigned a color from the gradient between minColor and maxColor.
    # json.dump(root.category, args.output, cls=CategoryEncoder, indent=2, separators=(',', ': '))
    json.dump(enumerate_category_tree(root), args.output, indent=2, separators=(',', ': '))
