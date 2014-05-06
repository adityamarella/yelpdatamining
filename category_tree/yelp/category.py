from recordtype import recordtype

# Category = recordtype('Category', [
#                                    'alias',
#                                    'category',
#                                    'title'
#                                   ],
#                       default=None)

class Category(object):
    """Category(alias, title, category)"""

    def __init__(self, alias=None, title=None, category=[]):
        self.alias = alias
        self.title = title
        self.category = [Category(**c) for c in category]
        self.businesses = set()

    # def __repr__(self):
    #     return "%s(alias=%r, title=%r, category=%r)" % (
    #         self.__class__.__name__,
    #         self.alias,
    #         self.title,
    #         self.category
    #     )

    def __repr__(self):
        return "%s(alias=%r, title=%r)" % (
            self.__class__.__name__,
            self.alias,
            self.title
        )

    @property
    def business_count(self):
        return len(self.businesses)
