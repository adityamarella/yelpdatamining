#!/usr/bin/env python

import random
import numpy
import vocabulary
from lda import LDA, lda_learning
from query_helper import TermCloud,QueryHelper


class LDATopics(TermCloud):
    
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
            """%(self.TABLE_NAME)]
         
        for stmt in stmts:
            self.query_helper.run_query(stmt)
         
        self.query_helper.commit()

    def process(self):
        categories = self.get_all_categories()
        for i,category in enumerate(categories):
            reviews = self.review_supplier.get_reviews(category)
            #if len(reviews) > 500:
            #    random.shuffle(reviews)
            #    reviews = reviews[:500]
            corpus = vocabulary.load_sentences(reviews)

            voca = vocabulary.Vocabulary(True)
            docs = [voca.doc_to_ids(doc) for doc in corpus]
            try:
                l = LDA(10, 0.5, 0.5, docs, voca.size(), False)
                lda_learning(l, 20, voca)
            except Exception, e:
                print "Error generating data for %d"%category 
            d = self.get_word_topic_dist(l, voca)
            import pdb; pdb.set_trace()
            self.insert_term_topic_frequencies(category, d)
            if i%10 == 0:
                print "%d finished"%i

    def get_word_topic_dist(self, lda, voca):
        zcount = numpy.zeros(lda.K, dtype=int)
        wordcount = [dict() for k in xrange(lda.K)]
        for xlist, zlist in zip(lda.docs, lda.z_m_n):
            for x, z in zip(xlist, zlist):
                zcount[z] += 1
                if x in wordcount[z]:
                    wordcount[z][x] += 1
                else:
                    wordcount[z][x] = 1

        phi = lda.worddist()

        ret = [None]*lda.K
        for k in xrange(lda.K):
            #print "\n-- topic: %d (%d words)" % (k, zcount[k])
            ret[k] = []
            for w in numpy.argsort(-phi[k])[:20]:
                #print "%s: %f (%d)" % (voca[w], phi[k,w], wordcount[k].get(w,0))
                ret[k].append((voca[w], round(phi[k,w]*1000)))

        return ret

if __name__=='__main__':

    import optparse
    yelp_db_path = "yelp.db"
    query_helper = QueryHelper(yelp_db_path)

    l = LDATopics(query_helper)
    l.process()

    query_helper.close()

