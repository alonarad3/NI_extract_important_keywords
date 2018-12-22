import pandas

from home_assigmetns import textProcessing


## moudle allows operation in candidates and their respective predictors , such as merge,remove, scoring and etc'....
def mergeKeywordsFromSeveralSourcesByStemming(alg_to_candidates_and_candiates_predictors):
    ### improve by bucketization
    stemmed_candidate_to_candidate = {} ## place stemmed object
    stemmed_candidate_to_alg_to_predictors = {}
    for alg,(candidates,candidates_predictors) in alg_to_candidates_and_candiates_predictors.iteritems():
        for candidate in candidates:
            stemmed_candidate = textProcessing.stemming(candidate)
            stemmed_candidate_to_candidate.setdefault(stemmed_candidate,"")
            if len(stemmed_candidate_to_candidate[stemmed_candidate])<len(candidate):
                stemmed_candidate_to_candidate[stemmed_candidate] = candidate
            stemmed_candidate_to_alg_to_predictors.setdefault(stemmed_candidate,{})
            stemmed_candidate_to_alg_to_predictors[stemmed_candidate].setdefault(alg)
            stemmed_candidate_to_alg_to_predictors[stemmed_candidate][alg] = candidates_predictors[candidate]
    merged_candidates = stemmed_candidate_to_candidate.values()
    merged_candidate_to_alg_to_predictors = {merged_candidate:stemmed_candidate_to_alg_to_predictors[textProcessing.stemming(merged_candidate)] for merged_candidate in merged_candidates}
    return merged_candidates,merged_candidate_to_alg_to_predictors

def removeKeywords(candidates,candidates_predictors,general_stemmed_keywords_arg=None):
    if not general_stemmed_keywords_arg:
        general_stemmed_keywords_arg = "tech_crunch_general"
    general_keywords = _getGeneralKeywords(general_stemmed_keywords_arg)
    approved_candidates = set()
    for candidate in candidates:
        candidate_predictors = candidates_predictors[candidate]
        processed = False
        ### ignore general keywords
        if not processed and textProcessing.stemming(candidate) in general_keywords :
            processed = True
        ### with wiki-page candidates
        if not processed and candidate_predictors["global"]["wiki_page"]:
            approved_candidates.add(candidate)
        ### both rake and title found that keyword relevant:
        if not processed and candidate_predictors.get("title_nc") and candidate_predictors.get("content_rake"):
            approved_candidates.add(candidate)
            processed = True
        if not processed and candidate_predictors.get("title_nc"):
            title_predictors = candidate_predictors["title_nc"]
            if _approveByTitlePredictors(title_predictors):
                approved_candidates.add(candidate)
                processed = True
        if not processed and candidate_predictors.get("content_rake"):
            rake_predictors = candidate_predictors["content_rake"]
            if _approveByRakePredictors(rake_predictors):
                approved_candidates.add(candidate)
                processed = True
    return approved_candidates
        
def _approveByTitlePredictors(title_predictors):
    if title_predictors.get("entity_label"):
        return True
    return False

APPROVED_POS_SET = set([u'NOUN',u'PROPN',u'ADJ'])

def _approveByRakePredictors(rake_predictors):
    pos_in_phrase = set([pos_list[0] for pos_list in rake_predictors["pos_tagging"]]) ## not very reptitve so its fine to take the first element
    if pos_in_phrase.intersection(APPROVED_POS_SET):
        if rake_predictors["rake_score"]/(1.0*rake_predictors["phrase_length"])>2.0:
            return True
    return False

GENERAL_WORDS = ["company","years","months","days","employees","techcrunch","pepole"]

def _getGeneralKeywords(general_stemmed_keywords_arg):
    """ create implementation of getting general words, e.g from DB by some tf-idf and argument,
    currently implemented in naive way"""
    return [textProcessing.stemming(word) for word in GENERAL_WORDS]


def getCandidatePredictorsAsDF(candidates_predictors,article_id=None):
    """ candidates_predictors is shaped as {candidate : {alg : {"predictor":dat}}}"""
    if not article_id:
        article_id = 0
    candidates = candidates_predictors.keys()
    multi_index = [[article_id]*len(candidates_predictors),candidates]
    vals = []
    for candidate in candidates:
        alg_to_predictors_dict = candidates_predictors[candidate]
        for alg,predictors_dict in alg_to_predictors_dict.iteritems():
            vals.append({(alg+"_"+k):v for k,v in predictors_dict.iteritems()})
    return pandas.DataFrame(vals,index=multi_index)
    

