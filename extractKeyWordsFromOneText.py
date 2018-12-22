import copy
from pprint import pprint as pp
from time import time


import RAKE
from gensim.summarization import keywords
import numpy
import pandas
from serializers import JsonSerializer
import unidecode

from home_assigmetns import textProcessing, candidatesUtils, \
    ValidationPredictors
from home_assigmetns.textProcessing import splitToSentences, cleanChunk

import warnings
warnings.filterwarnings("ignore") ## all warnings are not mine, needs neater solution

r2 = RAKE.Rake(RAKE.SmartStopList())


def doRakeTitle(text):
    keywords = r2.run(text, minCharacters=1, maxWords=4, minFrequency=1)
    return keywords

def doRake2(text):
    text = unicode(text)
    keywords =r2.run(text, minCharacters=3, maxWords=5, minFrequency=2)
    return keywords
    
def doTextRank(text):
    print keywords(text).split('\n')

def getRakeCandidates(title,atricle_content,predictors = False):
    text = " ".join([title] + atricle_content)
    text = text.replace("--", ",") ### any kind of preProcessing is welcomed here
    keywords =r2.run(text, minCharacters=3, maxWords=5, minFrequency=2)
    keywords = _mergeKeywords(keywords)
    candidates = _trimRakeKeywordsByScores(keywords)
    candidates = set([unicode(candidate) for candidate in candidates])  
    if predictors:
        candidatesToPredictors = {}
        keywordsToScore = dict(keywords)
        for candidate in candidates:
            candidatesToPredictors.setdefault(candidate,{})
            candidatesToPredictors[candidate].update({"in_title":candidate in title.lower(),
                                                      "rake_score":keywordsToScore[candidate],
                                                      "phrase_length":len(candidate.split())})
            ## add VERB / entity recognition from spacy.
            nlp_results = textProcessing.parseTextWithSpacy(candidate)
            for entity,entity_label_list in nlp_results["entity_recogintion"].iteritems():
                candidatesToPredictors[candidate].setdefault("entity_label_list",[])
                candidatesToPredictors[candidate]["entity_label_list"] += entity_label_list
            candidatesToPredictors[candidate].update({"pos_tagging":nlp_results["pos"].values()})
        return candidates,candidatesToPredictors
    return candidates


def _trimRakeKeywordsByScores(keywords):
    scores = numpy.array([s for kw,s in keywords])
    bar = 1.0 # can insert something dynamic later on
    return set([kw for kw,s in keywords if s>bar])


def _mergeKeywords(keywords):
    ### do stemming to merge keywords that repeated more than once, and add their scores,maybe add contains later
    stemmed_keywords = {}
    for keyword,score in keywords:
        stemmed_keyword = textProcessing.stemming(keyword)
        stemmed_keywords.setdefault(stemmed_keyword,["",0])
        stemmed_keywords[stemmed_keyword][1] += score
        if len(keyword)>= len(stemmed_keywords[stemmed_keyword][0]):
            stemmed_keywords[stemmed_keyword][0]=keyword
    return sorted([(keyword,score) for keyword,score in stemmed_keywords.values()],key=lambda x: x[1], reverse=True)

INCLUDE_NC_DEP = [u'nsubj',u'dobj',u'pobj']

INCLUDE_ENTITIES_TYPE = [u'PERSON',u'ORG',u'FAC',u'PRODUCT',u'GPE',u'EVENT']
EXCLUDE_ENTITIES_TYPE = [u'DATE',u'TIME',u'PERCENT',u'QUANTITY']

def getNounChunksAndEntitiesCandidates(sentence,predictors = False):
    """ iter over nounChunks and return the value according to the rule of the nounChunk in the sentence,
    same done for entities"""
    candidates = set() ### pred: dep
    if predictors:
        candidatesToPredictors = {}  
    nlp_results = textProcessing.parseTextWithSpacy(sentence)
    for chunk_text,chunck_dep_and_head_list in nlp_results["chunks"].iteritems():
        for dep,root_head in chunck_dep_and_head_list:
            if dep in INCLUDE_NC_DEP:
                chunk_text_broken_list = textProcessing.tryBreakChunks(chunk_text)
                for chunk_text in chunk_text_broken_list:
                    candidate = _getCandidateFromChunkText(chunk_text,nlp_results["pos"])
                    candidates.add(candidate)
                    if predictors:
                        candidatesToPredictors.setdefault(candidate,{})
                        candidatesToPredictors[candidate].update({"dep":dep,"root_head":root_head})
    for entity,entity_label_list in nlp_results["entity_recogintion"].iteritems():
        for entity_label in entity_label_list:
            ## add related entities that the title is talking about them:
            if entity_label in INCLUDE_ENTITIES_TYPE and unidecode.unidecode(entity.lower()) not in RAKE.SmartStopList():
                entity = cleanChunk(entity)
                candidates.add(entity)
                if predictors:
                    candidatesToPredictors.setdefault(entity,{})
                    candidatesToPredictors[entity].update({"entity_label":entity_label})
            ### remove candidates that might be refering to objects that are not intersting:
            if entity_label in EXCLUDE_ENTITIES_TYPE:
                for candidate in copy.deepcopy(candidates):
                    if candidate in entity:
                        candidates.remove(candidate)
                        if predictors:
                            candidatesToPredictors[candidate].update({"entity_label":entity_label})
    candidates = set([candidate for candidate in candidates if candidate])
    if predictors:
        return candidates,candidatesToPredictors
    return candidates

def _getCandidateFromChunkText(chunk_text,pos_tagging):
    chunk_text = textProcessing.cleanChunk(chunk_text)
    chunk_text = textProcessing.leaveOnlyNounsAndAdj(chunk_text,pos_tagging)
    ## nsubj - is the subject , and dobj is the direct object of a verb-> in title such as <x> lifts <z> 
    chunk_text = " ".join([token_text for token_text in chunk_text.split() if unidecode.unidecode(token_text) not in RAKE.SmartStopList()])
    return chunk_text

def getNounChunksOnText(text):
    sentences = splitToSentences(text)
    for sentence in sentences:
        print sentence
        print getNounChunksAndEntitiesCandidates(sentence)

PREDICTORS_DF = pandas.DataFrame()

def run(title,article_content,article_id,save_predictors = False):
    start = time()
    title_NC_candidates, title_predictors = getNounChunksAndEntitiesCandidates(title, predictors=True)
    rake_article_candidates,rake_article_predictors = getRakeCandidates(title,article_content,predictors=True)
    candidates,candidates_predictors = candidatesUtils.mergeKeywordsFromSeveralSourcesByStemming({"title_nc":(title_NC_candidates, title_predictors),
                                                                                                    "content_rake":(rake_article_candidates,rake_article_predictors)})
    for candidate in candidates_predictors.keys():
        candidates_predictors[candidate].setdefault("global")
        candidates_predictors[candidate]["global"] = ValidationPredictors.getPredictorsDict(candidate)
    if save_predictors:
        global PREDICTORS_DF 
        PREDICTORS_DF = PREDICTORS_DF.append(candidatesUtils.getCandidatePredictorsAsDF(candidates_predictors, article_id))
    candidates = candidatesUtils.removeKeywords(candidates,candidates_predictors)
    end = time()
    print "it took {x} seconds".format(x=end-start)
    return candidates
    
    
    
if __name__ == '__main__':
    dat = pandas.read_csv(r"C:\Users\Alon Arad\Documents\NI\articles_dat.csv")
    for i,article in dat.iterrows():
        print "#################"
        print "#################"
        print article.title
        article_content = JsonSerializer.deserialize(article.article_content)
        print "extracted keywords :"
        print run(article.title,article_content,article.article_id,True)
        print "tags :"
        print JsonSerializer.deserialize(article.tech_crunch_tags)
    print "done, can print predictors_df now"
    pass