import wikipedia
from home_assigmetns import textProcessing

TEXT_TO_WIKI_PAGE = {}

def hasWikepdiaPage(text):
    try:
        wikiPage = wikipedia.page(text)
        TEXT_TO_WIKI_PAGE.setdefault(text)
        TEXT_TO_WIKI_PAGE[text] = wikiPage
        return True
    except:
        return False

def getWikepdiaCategories(text):
    if TEXT_TO_WIKI_PAGE.get(text):
        return TEXT_TO_WIKI_PAGE[text].categories
    else:
        if hasWikepdiaPage(text):
            return TEXT_TO_WIKI_PAGE[text]
    return "No Page"

def getAppearncesFrequency(text):
    pass

def hasHyperLink(text,word_phrase_to_ref_link):
    if word_phrase_to_ref_link:
        for word_phrase in word_phrase_to_ref_link.keys():
            if text in word_phrase:
                return True
    return False

def approveByTitlePredictors(candidate,title_predictors):
    if title_predictors.get("entity_label"):
        return True
    return False

APPROVED_POS_SET = set([u'NOUN',u'PROPN',u'ADJ'])
DISALLOWED_ENTITY_LABELS = set([u'CARDINAL',u'DATE',u'PERCENT',u'ORDINAL'])

GENERAL_WORDS = ["company","brand","years","months","days","night","employees","techcrunch"
                 ,"people","wrong","right","time","minute","second","users","question","business","product","things","stuff",
                 "easy","hard"]
GENERAL_STEMMED_KEYWORD_ARG_TO_WORD_LIST = {"tech_crunch_general":[textProcessing.stemming(w) for w in GENERAL_WORDS]}

def removeGeneralWords(candidate,general_stemmed_keyword_arg=None):
    if not general_stemmed_keyword_arg:
        ## create implementation of getting general words, e.g from DB by some tf-idf and argument, maybe add wordnet
        ##currently implemented in naive way
        general_stemmed_keyword_arg = "tech_crunch_general"
    general_keywords = GENERAL_STEMMED_KEYWORD_ARG_TO_WORD_LIST[general_stemmed_keyword_arg] ## can implement a get
    if textProcessing.stemming(candidate) in general_keywords:
        return True
    return False

def removeByRakePredictors(candidate,rake_predictors):
    if rake_predictors.get("entity_label_list"):
        if set(rake_predictors["entity_label_list"]).intersection(DISALLOWED_ENTITY_LABELS):
            return True
    return False

def approveByRakePredictors(candidate,rake_predictors,bar = 1.6):
    pos_in_phrase = set([pos_list[0] for pos_list in rake_predictors["pos_tagging"]]) ## not very reptitve so its fine to take the first element
    if len(pos_in_phrase)>len(pos_in_phrase.intersection(APPROVED_POS_SET)):
        if rake_predictors["rake_score"]/(1.0*rake_predictors["phrase_length"])>bar and rake_predictors["in_title"]:
            return True
        return False
    if rake_predictors["in_title"]:
        return True
    if rake_predictors["rake_score"]/(1.0*rake_predictors["phrase_length"])>bar:
        return True
    return False

def getWikiTitle(candidate):
    if hasWikepdiaPage(candidate):
        return TEXT_TO_WIKI_PAGE[candidate].title ## returns wiki's title
    return ""

def getPredictorsDict(text,word_phrase_to_ref_link=None):
    results = {"wiki_page":hasWikepdiaPage(text),
               "hyper_linked":hasHyperLink(text, word_phrase_to_ref_link)}
    return results