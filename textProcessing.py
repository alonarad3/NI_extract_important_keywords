from collections import OrderedDict
import re

import en_core_web_sm
from gensim.models import phrases
from gensim.summarization import textcleaner
from gensim.utils import tokenize
from gensim.parsing.porter import PorterStemmer

POS = "pos"
DEP ="dep"
ENTITY_RECOGNITION = "entity_recogintion"
CHUNKS = "chunks"

nlp = en_core_web_sm.load()

def splitToSentences(text):
    return textcleaner.split_sentences(text)


porterStemmer = PorterStemmer()
def stemming(text):
    if len(text.split())==1:
        return porterStemmer.stem(text)
    return porterStemmer.stem_sentence(text)


def getTokenizedSentences(text):
    sentences = splitToSentences(text)
    tokenized_sentences = []
    for sentence in sentences:
        tokenized_sentence = [token for token in tokenize(sentence, lower=True)]
        tokenized_sentences.append(tokenized_sentence)
    return tokenized_sentences

bigram_phrases = phrases.Phrases(min_count=1,threshold=1)

def getbigramTokenizedSentences(text):
    """ note that this is an on going implemetation, thus order of articles might change the results"""
    tokenized_sentences = getTokenizedSentences(text)
    bigram_phrases.add_vocab(tokenized_sentences)
    bigram_sentences = [bigram_phrases[sentence] for sentence in tokenized_sentences]
    return bigram_sentences

def getWordAndBigrams2Freq(text):
    tokenized_sentences = getTokenizedSentences(text)
    bigram_phrases.add_vocab(tokenized_sentences)
    return "nothing!"



def parseTextWithSpacy(text):
    """ gets text and retruns a dictionary by areas: 
    keys : [entity_recogintion,dep,pos,chucks], and by tokens, will be used to check qualities of tokens"""
    text = unicode(text)
    doc = nlp(text)
    resultParsing = {ENTITY_RECOGNITION:OrderedDict(),DEP:OrderedDict(),POS:OrderedDict(),CHUNKS:OrderedDict()}
    for token in doc:
        resultParsing[POS].setdefault(token.text,[])
        resultParsing[POS][token.text].append(token.pos_)
        resultParsing[DEP].setdefault(token.text,[])
        resultParsing[DEP][token.text].append((token.dep_,token.head.text))
    for ent in doc.ents:
        resultParsing[ENTITY_RECOGNITION].setdefault(ent.text,[])
        resultParsing[ENTITY_RECOGNITION][ent.text].append(ent.label_)
    for chunk in doc.noun_chunks:
        resultParsing[CHUNKS].setdefault(chunk.text,[])
        resultParsing[CHUNKS][chunk.text].append((chunk.root.dep_,chunk.root.head.text))        
    return resultParsing
    
def leaveOnlyNounsAndAdj(chunk_text,pos_tagging):
    nouns = []
    for token in nlp(chunk_text):
        if pos_tagging[token.text].pop() in [u'NOUN',u'PROPN',u'ADJ']:
            nouns.append(token.text)
    return " ".join(nouns)

moneyRegEx = r"\$\d+(?:\.\d+){0,1}[mMbB]"
invalidChars = ["\$","\?","\-","\#","\\","\'",'\"',"\*","\%","\(","\)","\'s$"]
invalidCharsReg = r"(" + r"|".join(invalidChars) + r")"

def cleanChunk(chunk_text):
    """ remove patterns that are not fitting for important keywords """ 
    regexes = [moneyRegEx,invalidCharsReg]
    for regex in regexes:
        chunk_text = re.sub(regex," ",chunk_text)
    chunk_text = chunk_text.replace("  "," ").replace("  "," ").replace("  "," ")
    chunk_text = chunk_text.strip()
    return chunk_text

breakPatterns = [r"\'s",r"and"]

def tryBreakChunks(chunk_text):
    chunk_text = re.split("|".join(breakPatterns), chunk_text)
    return chunk_text


if __name__ == '__main__':
    from pprint import pprint as pp
    titleText = "Flux raises $7.5M Series A to bring its digital receipts platform to more banks and merchants"
    titleText2 = "WhatsApp has an encrypted child porn problem"
    x = parseTextWithSpacy(titleText)
    x2 = parseTextWithSpacy(titleText2)
    pp(x)
    pp(x2)
  

    
