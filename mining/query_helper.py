from collections import deque
import json
import sqlite3
import sys

class QueryHelper(object):

    def __init__(self, yelp_db_path="yelp.db"):
        self.conn = sqlite3.connect(yelp_db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def run_query(self, query, bindings=[]):
        self.cursor.execute(query, bindings)
        rows = self.cursor.fetchall()
        return rows

    def commit(self):
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

class ReviewSupplier(object):

    def __init__(self, query_helper):
        self.query_helper = query_helper

    def get_reviews(self, category_id = -1):

        stmt = "SELECT B.id, R.review FROM\
                    businesses as B, reviews as R, categories_businesses as CB\
                WHERE B.id=CB.business_id and R.business_id = B.id and CB.category_id=?"
        values = [category_id]
        rows = self.query_helper.run_query(stmt, values)
        
        return [row[1] for row in rows]


class Category(object):
    """
    The following three attributes define this datastructure
    category_id: id of the category given in categories table
    title: category title
    children: is a list of Category objects
    """

    def __init__(self, cid = -1, title="", business_count=0):
        self.category_id = cid
        self.title = title
        self.business_count = business_count
        self.parent = None
        self.children = []

    def __repr__(self):
        return '{"category":%r,"alias":%r, "title":%r}' % (
            [child for child in self.children],
            self.category_id,
            self.title,
        )

class CategoryEncoder(json.JSONEncoder):
    """A JSONEncoder for Category.
    """
    def default(self, obj):
        if isinstance(obj, Category):
            return {'alias': obj.category_id,
                    'title': obj.title,
                    'category': obj.children
                   }
        # Let the base class default method raise the TypeError
        return super().default(self, obj)

class CategoryTreeCreator(object):

    def __init__(self, query_helper=None):
        self.query_helper = query_helper

    def create_category_tree(self):
        """
        This function creates load the categories_subcategories into
        a category tree datastructure.
        """
        stmt = "SELECT \
                    C.id, C.title, cs.subcategory_id\
                FROM categories as C \
                    LEFT OUTER JOIN categories_subcategories as cs ON C.id = cs.category_id"
        rows = self.query_helper.run_query(stmt)

        categories = {}
        for row in rows:
            arr = categories.setdefault(row[0], {})
            arr['title'] = row[1]
            arr['tree'] = Category(cid=row[0], title=row[1])
            if row[2] != None:
                arr.setdefault('values', []).append(row[2])

        subcategories_union = set([])
        for k,v in categories.iteritems():
            values = v.get('values', [])
            tree = v["tree"]
            for cid in values:
                subcategories_union.add(cid)
                child_node = categories[cid]['tree']
                tree.children.append(child_node)


        #find the top level nodes of the category hierarchy
        #Top level nodes can be computed by doing a set-difference between
        #set of all categories and the set of union of all subcategories
        categories_union = set(categories.keys())
        top_level_nodes = categories_union.difference(subcategories_union)

        #create a root node and append the top level node to the root node to
        #complete the tree construction
        root = Category(cid=-1, title="All")
        for cid in top_level_nodes:
            root.children.append(categories[cid]['tree'])

        #set parent node
        self.setparent(root, None)

        #remove child if child.parent != currentnode
        self.deduplicate(root)

        # count the businesses for all the nodes
        self.count_businesses(root)

        return root

    def setparent(self, node, parent):
        """
        do inorder traversal to set the parent;
        all child nodes should have correct parent before
        the current node has a parent
        """
        for child in node.children:
            self.setparent(child, node)

        node.parent = parent

    def deduplicate(self, node):
        node.children = [ child for child in node.children if child.parent==node]
        for child in node.children:
            self.deduplicate(child)

    def count_businesses(self, root):
        stmt = """SELECT
                    c.id, count(cb.business_id) AS business_count
                  FROM categories AS c
                  LEFT JOIN categories_businesses AS cb
                    ON (cb.category_id = c.id)
                  GROUP BY c.id;"""
        rows = self.query_helper.run_query(stmt)
        business_counts = {r[0]: r[1] for r in rows}

        # traverse tree to update categories
        categoryStack = []
        node = root
        while node is not None:
            try:
                node.business_count = business_counts[node.category_id]
            except KeyError:
                if node is root:
                    pass
                else:
                    print "Error: unable to find count for {}".format(node)

            categoryStack.extend(node.children)
            try:
                node = categoryStack.pop()
            except IndexError:
                node = None

class TermCloud(object):
    
    def __init__(self, query_helper):
        self.TABLE_NAME = self.__class__.__name__.lower()
        self.query_helper = query_helper
        self.review_supplier = ReviewSupplier(self.query_helper)
        self.create_table()

    def create_table(self):
        stmts = ["""
            CREATE TABLE IF NOT EXISTS %s (
                id INTEGER,
                term TEXT,
                freq REAL,
                category_id INTEGER,

                PRIMARY KEY (id),
                FOREIGN KEY (category_id) REFERENCES categories(id)

            );
            """%(self.TABLE_NAME),
            """
            CREATE TABLE IF NOT EXISTS %s_context (
                term_id INTEGER,
                business_id INTEGER,
                context TEXT,

                FOREIGN KEY (term_id) REFERENCES %s(id),
                FOREIGN KEY (business_id) REFERENCES businesses(id)
            );
            """%(self.TABLE_NAME, self.TABLE_NAME)]
         
        for stmt in stmts:
            self.query_helper.run_query(stmt)
         
        self.query_helper.commit()

    def get_all_categories(self):
        stmt = "select id from categories"
        rows = self.query_helper.run_query(stmt)
        return [row[0] for row in rows]

    def insert_term_frequencies(self, category_id, freq_dict, topic_id=None):
        projection = ['term', 'freq', 'category_id']
        if topic_id!=None:
            projection.append('topic_id')

        for term,freq in freq_dict.iteritems():
            values = [term, freq, category_id]
            if topic_id!=None:
                values.append(topic_id)
            self.query_helper._insert(self.TABLE_NAME, 
                    projection,
                    values)
        self.query_helper.commit()
    
    def insert_term_topic_frequencies(self, category_id, distribution):
        projection = ['term', 'freq', 'category_id', 'topic_id']
        for topic_id, item in enumerate(distribution):
            for i,(term,freq) in enumerate(item):
                values = [term, freq, category_id, topic_id]
                self.query_helper._insert(self.TABLE_NAME, 
                        projection,
                        values)
                if i>20:
                    break
        self.query_helper.commit()


def enumerate_category_tree(root):
    categories = [("category_id", "category_title", "parent_category", "business_count")]
    categoryQueue = deque([(root, None)])

    while len(categoryQueue) != 0:
        node, parent_title = categoryQueue.popleft()
        categories.append((node.category_id, node.title,
            parent_title, node.business_count))
        [categoryQueue.append((child, node.title)) for child in node.children]

    return categories

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--database', required=True,
                        help='the filename of the database containing the Yelp data')
    parser.add_argument('output', nargs='?', type=argparse.FileType('w'), default=sys.stdout,
                        help='write output to file')
    args = parser.parse_args()

    helper = QueryHelper(args.database)
    tree_creator = CategoryTreeCreator(helper)
    root = tree_creator.create_category_tree()
    helper.close()

    # json.dump(root.children, args.output, cls=CategoryTreeEncoder)
    json.dump(enumerate_category_tree(root), args.output, indent=2, separators=(',', ': '))
