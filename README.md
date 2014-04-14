##YELP! Visualization

#Goals
* Tell a story with the data
* Demonstrate and document use of the steps of the data pipeline
    - Propose question
    - Collect Data (or use chosen data set)
    - Clean Data
    - Explore Data
    - Use Data
        - Produce output
        - Provide interactive interface
        - Create visualizations

#IDEAS
* Topic Extraction and Visualization using LDA 
(refer http://research.microsoft.com/en-us/um/people/shliu/fp1162-liu.pdf)
  - What are the major topics in the customer feedback?
  - What are the most active topics during the last three months?
  - What are the key concepts mentioned in the above topics? 
  - How have the most active topics evolved over time?
  - For which meal is a given restaurant most popular?
  - What are the different topics given for open versus closed businesses?

* Word Cloud Visualization
(refer http://yatani.jp/paper/CHI2011.pdf)
  - collect adjective-noun word pairs
  - do sentiment analysis on the word pairs
  - visualize it


#REFERENCE

* LDA
  - http://shuyo.wordpress.com/2011/05/18/latent-dirichlet-allocation-in-python/
  - Topic Modeling Information: https://www.cs.princeton.edu/~blei/topicmodeling.html
  - Stanford Topic Modelling Toolbox - http://nlp.stanford.edu/downloads/tmt/tmt-0.4/
  - Mallet: http://mallet.cs.umass.edu/topics.php

* Sentiment Analysis
  - Google Cloud APIs - <a href="https://developers.google.com/prediction/docs/sentiment_analysis?_ga=1.226385882.1376685994.1395843476">Creating a sentiment analysis model</a>
  - <a href="http://sentiwordnet.isti.cnr.it/">SentiWordNet</a>
  - Stanford Sentiment Analysis - http://nlp.stanford.edu/sentiment/treebank.html

#NOTES
* Topic Analysis work
  - Only use businesses with 20 or greater reviews (yields 3636 businesses in data set)


