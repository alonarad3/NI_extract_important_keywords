import BeautifulSoup
import pandas
import textProcessing
import unidecode

from home_assigmetns import extractKeyWordsFromOneText, candidatesUtils
from home_assigmetns.parsingUtils import _getTextElement


class FeedArticle(object):
    def __init__(self,articleXML):
        self.title = unidecode.unidecode(articleXML.title.string)
        self.url = self._getURL(articleXML.link.string,articleXML.comments.string)
        self.tech_crunch_tags = [cat.string for cat in articleXML.find_all("category")]
        self.article_content, self.word_phrase_to_ref_link = self._getArticleContet(articleXML.encoded)  
        self.article_id = hash(self.title)
        self.important_keywords = self.getImportantKeywords()
        self.recall,self.presicion,self.f_score = self.evulateImportantKeywordsMetrics()
        
    def _getArticleContet(self,encodedTag):
        """ retruns a list of texts in pargraphs , and all the keywords with hyperlinks as a dict"""
        xmlEncodedTag = BeautifulSoup(encodedTag.string,"lxml")#encoded tag actually has a format of an XML
        articleContent = []
        for element in xmlEncodedTag.body.contents:
            if _getTextElement(element):
                articleContent.append(unidecode.unidecode(element.get_text()))
            if self._isEndOfArticleCommerical(element):
                    continue
        wordPhraseToRefLink = {a.get_text().strip().lower():a.attrs['href'] for a in xmlEncodedTag.find_all("a")}
        return articleContent,wordPhraseToRefLink
    
    def _isEndOfArticleCommerical(self,element):
        if element.name == "div":
                if element.attrs.get('class') == ['embed','breakout']: ## means we are getting content from somewhere else
                    return True
        return False
    
    def _getURL(self,proxyLink,commentsLink):
        ## for some reason going with proxy is more stable 
        ### can also be name +?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+Techcrunch+%28TechCrunch%29&utm_content=FeedBurner
        return proxyLink
    
    def getAsPandasSeries(self):
        return pandas.Series(self.__dict__)
    
    def getImportantKeywords(self,num_threshold=None):
#         start = time()
        candidates,candidates_predictors = self._getCandidatesByExtractMethods()
        candidates = self._removeKeywords(candidates,candidates_predictors)
        if num_threshold:
            candidates_and_scores = self._calcScores(candidates,candidates_predictors) ## return sorted
            return [candidate for candidate,score in candidates_and_scores[:num_threshold]]
#         end = time()
#         print "it took {x} seconds to get important Keywords for article".format(x=round(end-start))
        return candidates
    
    def _getCandidatesByExtractMethods(self):
        title_NC_candidates, title_predictors = extractKeyWordsFromOneText.getNounChunksAndEntitiesCandidates(self.title, predictors=True)
        rake_article_candidates,rake_article_predictors = extractKeyWordsFromOneText.getRakeCandidates(self.title,self.article_content,predictors=True)
        candidates,candidates_predictors = candidatesUtils.mergeKeywordsFromSeveralSourcesByStemming({"title_nc":(title_NC_candidates, title_predictors),
                                                                                                    "content_rake":(rake_article_candidates,rake_article_predictors)})
        return candidates,candidates_predictors
    
    def _calcScores(self,candidates,candidates_predictors):
        pass
    
    def _removeKeywords(self,candidates,candidates_predictors):
        """ apply rules to eliminate keywords that are bit actually keywords"""
        return candidatesUtils.removeKeywords(candidates,candidates_predictors)
    
    def evulateImportantKeywordsMetrics(self,tags=None):
        ### very shallow implementation of recall/precision measurments,returns True_positive,False_Postive, False Negative
        results = {"True_Positive":0,"False_Positive":0,"False_Negative":0}
        if not tags:
            tags = [tag for tag in self.tech_crunch_tags if tag not in [u"TC",u"Column"]]
        if not tags:
            return pandas.Series({"recall":None,"precision":None,"f_score":None})
        stemmed_tags = [textProcessing.stemming(tag) for tag in tags]
        stemmed_keywords = [textProcessing.stemming(candidate) for candidate in self.important_keywords]
        for stemmed_keyword in stemmed_keywords:
            if stemmed_keyword in stemmed_tags:
                results["True_Positive"]+=1
            else:
                results["False_Positive"]+=1
        results["False_Negative"] = len(set(stemmed_tags).difference(set(stemmed_keywords)))
        if not stemmed_tags:
            recall = None
        else:
            recall = results["True_Positive"]*1.0/len(stemmed_tags)
        if results["True_Positive"]+results["False_Positive"] == 0:
            precision = None
        else:
            precision = results["True_Positive"]*1.0 / (results["True_Positive"]+results["False_Positive"])
        if recall and precision:
            f_score = 2*(precision*recall)/(precision+recall)
        else:
            f_score =None
        return recall,precision,f_score