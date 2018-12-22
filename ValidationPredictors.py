import wikipedia

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

def getPredictorsDict(text,word_phrase_to_ref_link=None):
    results = {"wiki_page":hasWikepdiaPage(text),
               "hyper_linked":hasHyperLink(text, word_phrase_to_ref_link)}
    return results