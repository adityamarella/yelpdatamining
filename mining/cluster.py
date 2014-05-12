
import os
import random
import numpy
import vocabulary
from query_helper import TermCloud,QueryHelper


class YelpCluster(TermCloud):
    
    def __init__(self, query_helper):
        TermCloud.__init__(self, query_helper)
    
    def create_table(self):
        stmts = ["""
            CREATE TABLE IF NOT EXISTS %s (
                id INTEGER,
                term TEXT,
                freq REAL,
                topic_id INTEGER,
                category_id INTEGER,

                PRIMARY KEY (id),
                FOREIGN KEY (category_id) REFERENCES categories(id)

            );
            """%(self.TABLE_NAME),
            """PRAGMA encoding = "UTF-8"; """]
         
        for stmt in stmts:
            self.query_helper.run_query(stmt)
         
        self.query_helper.commit()

    def process(self):
        categories = self.get_all_categories()
        for i,category in enumerate(categories):
            if i<51:
                continue
            reviews = self.review_supplier.get_reviews(category)
            if len(reviews) > 1000:
                random.shuffle(reviews)
                reviews = reviews[:1000]

            fp = open("tmp", "w")
            for review in reviews:
                fp.write("%s\n"%review.encode('utf-8'))
            fp.close()
            
            os.system("./wcluster --text tmp --c 50")

            distribution = {}
            output_file_path = "tmp-c50-p1.out/paths"
            fp = open(output_file_path)
            for line in fp:
                c,term,freq = tuple(line.strip().split())
                term = unicode(term, "UTF-8")
                c = int(c, 2)
                freq = int(freq)
                distribution.setdefault(c, []).append((term, freq))
            fp.close()
            self.insert_cluster_term_frequencies(category, distribution)
            print "i=%d, cat=%d"%(i, category)


if __name__=='__main__':

    import optparse
    yelp_db_path = "yelp.db"
    query_helper = QueryHelper(yelp_db_path)

    l = YelpCluster(query_helper)
    l.process()

    query_helper.close()

