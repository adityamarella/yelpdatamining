import json
import sqlite3
import sys

class CategoryTree(object):
    """
    The following three attributes define this datastructure
    category_id: id of the category given in categories table
    title: category title
    children: is a list of CategoryTree objects
    """

    def __init__(self, cid = -1, title=""):
        self.category_id = cid
        self.title = title
        self.parent = None
        self.children = []

    def __repr__(self):
        return '{"category":%r,"alias":%r, "title":%r}' % (
            [child for child in self.children],
            self.category_id,
            self.title,
        )

class CategoryTreeEncoder(json.JSONEncoder):
    """A JSONEncoder for CategoryTree.
    """
    def default(self, obj):
        if isinstance(obj, CategoryTree):
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
            arr['tree'] = CategoryTree(cid=row[0], title=row[1])
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
        root = CategoryTree(cid=-1, title="All")
        for cid in top_level_nodes:
            root.children.append(categories[cid]['tree'])

        #set parent node
        self.setparent(root, None)

        #remove child if child.parent != currentnode
        self.deduplicate(root)

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

    json.dump(root.children, args.output, cls=CategoryTreeEncoder)
