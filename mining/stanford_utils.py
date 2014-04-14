import jpype
import os
import nltk
from jpype import *

STANFORD_TAGGER_DIR = "/usr/share/stanford-postagger"
STANFORD_PARSER_DIR = "/usr/share/stanford-parser"
STANFORD_NER_DIR = "/usr/share/stanford-ner"
stanford_parser_home = None

def startJvm():
    os.environ.setdefault("STANFORD_PARSER_HOME", STANFORD_PARSER_DIR)
    global stanford_parser_home
    stanford_parser_home = os.environ["STANFORD_PARSER_HOME"]
    jpype.startJVM(jpype.getDefaultJVMPath(),\
            "-ea", "-Djava.class.path=%s/stanford-parser.jar:%s/stanford-parser-3.3.0-models.jar" % (stanford_parser_home, stanford_parser_home),)

startJvm() # one jvm per python instance.

class Tokenizer(object):

    def __init__(self):
        process = jpype.JPackage("edu").stanford.nlp.process
        self.process = process
        
        TokenizerFactory = process.TokenizerFactory
        CoreLabelTokenFactory = process.CoreLabelTokenFactory
        PTBTokenizer = process.PTBTokenizer
        self.tokenizerFactory = PTBTokenizer.factory(CoreLabelTokenFactory(), JString(""))

    def tokenize(self, paragraph):
        tokens = self.tokenizerFactory.getTokenizer(java.io.StringReader(paragraph)).tokenize()
        return [token.word() for token in tokens]

    def span_tokenize(self, paragraph):
        tokens = self.tokenizerFactory.getTokenizer(java.io.StringReader(paragraph)).tokenize()
        return [ (token.word(), token.beginPosition(), token.endPosition()) for token in tokens]

class POSTagger(object):

    def __init__(self, model='english-bidirectional-distsim.tagger'):
        self.stanford_tagger = nltk.tag.stanford.POSTagger(STANFORD_TAGGER_DIR + "/models/"+ model,\
                    STANFORD_TAGGER_DIR+'/stanford-postagger.jar', java_options="-mx1000m")

    def tag(self, words):
        return self.stanford_tagger.tag(words)

class Parser(object):

    def __init__(self, pcfg_model_fname=None):
        if pcfg_model_fname == None:
            #self.pcfg_model_fname = "%s/englishPCFG.ser" % stanford_parser_home
            #self.pcfg_model_fname = "%s/englishFactored.ser" % stanford_parser_home
            self.pcfg_model_fname = "edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"       
        else:
            self.pcfg_model_fname = pcfg_model_fname


        process = jpype.JPackage("edu").stanford.nlp.process
        self.process = process
        
        TokenizerFactory = process.TokenizerFactory
        CoreLabelTokenFactory = process.CoreLabelTokenFactory
        PTBTokenizer = process.PTBTokenizer
        
        ling = jpype.JPackage("edu").stanford.nlp.ling

        CoreLabel = ling.CoreLabel
        HasWord = ling.HasWord
        Sentence = ling.Sentence

        self.trees = jpype.JPackage("edu").stanford.nlp.trees
        TreePrint = self.trees.TreePrint
        Tree = self.trees.Tree
            
        LexicalizedParser = jpype.JPackage("edu").stanford.nlp.parser.lexparser.LexicalizedParser
        self.parser = LexicalizedParser.loadModel()
        self.parser.setOptionFlags(["-retainTmpSubcategories"])
        
        self.tokenizerFactory = PTBTokenizer.factory(CoreLabelTokenFactory(), JString(""))

    def parse(self, sentence):
        """
        Parses the sentence string, returning the tokens, and the parse tree as a tuple.
        tokens, tree = parser.parse(sentence)
        """
        tokens = self.tokenizerFactory.getTokenizer(java.io.StringReader(JString(sentence))).tokenize()
        for token in tokens:
            if token.word() in ["down"]:
                print "setting tag"
                token.setTag("IN")
                pass
            if token.word().lower() in ["bot"]:
                token.setTag("NN")
                pass
        
        return tokens, self.parser.parse(tokens)
   
    def parseDocument(self, filepath):
        """
          - efficiently parses a text file; 
          - use this function when you have a large text blob's.
          - stanford parser has a word limit of 80, anything more than that will consume lot of memory
          - large blob's could be written to tmp file and passed to this function

          @filepath path to the file containing the text blob
        """

        DocumentPreprocessor = self.process.DocumentPreprocessor
        documentPreprocessor = DocumentPreprocessor(JString(filepath))

        stringArray = JArray(JString, 1)
        arr = stringArray([".", ";", "!", "\n"])
        documentPreprocessor.setSentenceFinalPuncWords(arr)

        it = documentPreprocessor.iterator()
        offset = 0
        while it.hasNext():
            tokens = it.next()
            t = self.parser.parse(tokens)
            t.setSpans()
            yield tokens, t

    def getIndicesForLabel(self, tokens, tree, lb="NP"):
        ret = []
        lst = self.getTreesForLabel(tree, "NP")
        for item in lst:
            ret.append( (tokens[item.getSpan().getSource()].beginPosition(), 1+tokens[item.getSpan().getTarget()].endPosition()) )
        return ret


    def getTreesForLabel(self, ptree, lb="NP"):
        import pdb; pdb.set_trace()
        if ptree.label().value() == lb:
            return [ptree]

        ret = []
        children = ptree.children()
        
        for child in children:
            ret.extend(self.getTreesForLabel(child))
     
        return ret
        
