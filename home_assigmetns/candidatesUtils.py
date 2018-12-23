import pandas

from home_assigmetns import textProcessing, ValidationPredictors


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


APPROVE_FUNCTIONS_AND_NAME = [
    (ValidationPredictors.approveByRakePredictors,"content_rake"),
    (ValidationPredictors.approveByTitlePredictors,"title_nc")
    ]

REMOVE_FUNCTIONS_AND_NAME =[
    (ValidationPredictors.removeByRakePredictors,"content_rake")
    ]

def removeKeywords(candidates,candidates_predictors,remove_functions_and_name=REMOVE_FUNCTIONS_AND_NAME,approve_functions_and_names = APPROVE_FUNCTIONS_AND_NAME,general_stemmed_keywords_arg=None):
    approved_candidates = set()
    wiki_approvals = 0
    candidates = sorted(list(candidates),key=lambda x: len(x),reverse = True) ## check wiki first for longer phrases - rake style 
    stemmed_candidates = [textProcessing.stemming(candidate) for candidate in candidates]
    for candidate in candidates:
        candidate_predictors = candidates_predictors[candidate]
        processed = _removeCandidate(candidate,candidate_predictors,remove_functions_and_name,general_stemmed_keywords_arg) 
        if not processed: ## if removed no point in validation
            processed, wiki_approvals = _approveCandidate(candidate, candidate_predictors, approve_functions_and_names,wiki_approvals,stemmed_candidates)
            if processed:
                approved_candidates.add(candidate)
    return approved_candidates

def _removeCandidate(candidate,candidate_predictors,remove_functions_and_name,general_stemmed_keywords_arg):
    removed = False
    removed = ValidationPredictors.removeGeneralWords(candidate, general_stemmed_keywords_arg)
    if removed:
        return removed
    for func,arg_name in remove_functions_and_name:
        if candidate_predictors.get(arg_name):
            removed = func(candidate,candidate_predictors[arg_name])
        if removed:
            return removed
    return removed
                    
def _approveCandidate(candidate,candidate_predictors,approve_functions_and_names,wiki_approvals,stemmed_candidates):
    approved = False
    for func,arg_name in approve_functions_and_names:
        if not approved and candidate_predictors.get(arg_name):
            approved = func(candidate,candidate_predictors[arg_name])
    if not approved and wiki_approvals<4: ## up to 4 wiki_approvals to run in a reasonable time
        wiki_title = ValidationPredictors.getWikiTitle(candidate)
        if textProcessing.stemming(wiki_title) not in stemmed_candidates and wiki_title:
            approved = True
        wiki_approvals +=1
    return approved,wiki_approvals

def getCandidatePredictorsAsDF(candidates_predictors,article_id=None):
    """ candidates_predictors is shaped as {candidate : {alg : {"predictor":dat}}}"""
    if not article_id:
        article_id = 0
    candidates = candidates_predictors.keys()
    multi_index = [[article_id]*len(candidates_predictors),candidates]
    vals = []
    for candidate in candidates:
        alg_to_predictors_dict = candidates_predictors[candidate]
        vals_dict = {}
        for alg,predictors_dict in alg_to_predictors_dict.iteritems():
            vals_dict.update({(alg+"_"+pred):pred_val for pred,pred_val in predictors_dict.iteritems()})
        vals.append(vals_dict)
    return pandas.DataFrame(vals,index=multi_index)
    

