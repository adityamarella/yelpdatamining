#!/usr/bin/env python

from __future__ import print_function
import collections
import json
import yelp
import os
from pprint import pprint
import sys


class CategoryTree(object):
    def __init__(self, io):
        self.categories = [yelp.category.Category(**c) for c in json.load(io)]

    def __repr__(self):
        return "%s(categories=%r)" % (
            self.__class__.__name__,
            self.categories
        )

    def search(self, alias=None, title=None):
        if alias is None and title is None:
            return None

        if alias is not None and title is not None:
            raise RuntimeError("Cannot search for both title and alias")

        categoryStack = [category for category in self.categories]
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


class CategoryTreeEncoder(json.JSONEncoder):
    """A JSONEncoder for CategoryTree.
    """
    def default(self, obj):
        if isinstance(obj, CategoryTree):
            return [category for category in obj.categories]
        elif isinstance(obj, yelp.category.Category):
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
    ct = CategoryTree(args.categories)

    # 2. count each business in each category and sub-category
    businesses = []
    for line in args.businesses:
        businesses.append(yelp.business.Business(**json.loads(line)))

    for business in businesses:
        for category_title in business.categories:
            # some category titles need to be cleaned and normalized
            category_title = normalize_category_title(category_title)

            try:
                category = ct.search(title=category_title)
                category.businesses.add(business)
            except AttributeError:
                # ignore all unknown categories
                # (see list in `normalize_category_title`)
                pass

    # 3. output category tree with business counts as JSON
    json.dump(ct, args.output, cls=CategoryTreeEncoder, indent=2, separators=(',', ': '))
