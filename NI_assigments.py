from bs4 import BeautifulSoup
import pandas
import requests
import unidecode
from time import time
from home_assigmetns import extractKeyWordsFromOneText, ValidationPredictors,candidatesUtils,\
    textProcessing
# import warnings
# warnings.filterwarnings("ignore") ## all warnings are not mine, needs neater solution

csv_path = r"C:\Users\Alon Arad\Documents\NI\articles_dat_2.csv"

def getXMLFeedAsListOfItems():
    articles =[]
    parsedXML = parseXMLPage()
    for article in parsedXML.find_all("item"):
        article = FeedArticle(article)
        end = time()
        print "title : ",article.title
        print "-------------------"
        print "url link : ",article.url
        print "-------------------"
        print "important keywords : ",article.important_keywords  
        articles.append(article)
    return articles    
 
def writeArticlesDatToCSV(articles,csvPath = csv_path):
    articles_df = pandas.DataFrame([article.__dict__ for article in articles],columns=["article_id","url","title","article_content","tech_crunch_tags","word_phrase_to_ref_link","important_keywords","metrics"])
    try:
        with open(csvPath, 'a') as f:
            articles_df.to_csv(f, header=False)
    except:
        articles_df.to_csv(csvPath)

def parseXMLPage(pageUrl="http://feeds.feedburner.com/TechCrunch/"):
    pageResponse = requests.get(pageUrl, timeout=5)
    pageParsedContent = BeautifulSoup(pageResponse.content,"xml")
    return pageParsedContent

def _getTextElement(element):
    """ return if a parsed html element containes text that is related to the article"""
    if element.name == "p":
        return element.get_text()
    return  ""

class FeedArticle(object):
    def __init__(self,articleXML):
        self.title = unidecode.unidecode(articleXML.title.string)
        self.url = self._getURL(articleXML.link.string,articleXML.comments.string)
        self.tech_crunch_tags = [cat.string for cat in articleXML.find_all("category")]
        self.article_content, self.word_phrase_to_ref_link = self._getArticleContet(articleXML.encoded)  
        self.article_id = hash(self.title)
        self.important_keywords = self.getImportantKeywords()
        self.metrics = self.evulateImportantKeywordsMetrics()
        
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
        start = time()
        candidates,candidates_predictors = self._getCandidatesByExtractMethods()
        candidates_predictors = self._addGlobalPredictors(candidates_predictors)
        candidates = self._removeKeywords(candidates,candidates_predictors)
        if num_threshold:
            candidates_and_scores = self._calcScores(candidates,candidates_predictors) ## return sorted
            return [candidate for candidate,score in candidates_and_scores[:num_threshold]]
        end = time()
        print "it took {x} seconds to get important Keywords for article".format(x=round(end-start))
        return candidates
    
    def _getCandidatesByExtractMethods(self):
        title_NC_candidates, title_predictors = extractKeyWordsFromOneText.getNounChunksAndEntitiesCandidates(self.title, predictors=True)
        rake_article_candidates,rake_article_predictors = extractKeyWordsFromOneText.getRakeCandidates(self.title,self.article_content,predictors=True)
        candidates,candidates_predictors = candidatesUtils.mergeKeywordsFromSeveralSourcesByStemming({"title_nc":(title_NC_candidates, title_predictors),
                                                                                                    "content_rake":(rake_article_candidates,rake_article_predictors)})
        return candidates,candidates_predictors
    
    def _calcScores(self,candidates,candidates_predictors):
        pass
    
    def _addGlobalPredictors(self,candidates_predictors):
        for candidate in candidates_predictors.keys():
            candidates_predictors[candidate].setdefault("global")
            candidates_predictors[candidate]["global"] = ValidationPredictors.getPredictorsDict(candidate, self.word_phrase_to_ref_link)
        return candidates_predictors
    
    def _removeKeywords(self,candidates,candidates_predictors):
        """ apply rules to eliminate keywords that are bit actually keywords"""
        return candidatesUtils.removeKeywords(candidates,candidates_predictors)
    
    def evulateImportantKeywordsMetrics(self,tags=None):
        ### very shallow implementation of recall/precision measurments,returns True_positive,False_Postive, False Negative
        results = {"True_Positive":0,"False_Postive":0,"False_Negative":0}
        if not tags:
            tags = [tag for tag in self.tech_crunch_tags if tag!=u"TC"]
        if not tags:
            return pandas.Series({"recall":None,"precision":None,"f_score":None})
        stemmed_tags = [textProcessing.stemming(tag) for tag in tags]
        stemmed_keywords = [textProcessing.stemming(candidate) for candidate in self.important_keywords]
        for stemmed_keyword in stemmed_keywords:
            if stemmed_keyword in stemmed_tags:
                results["True_Positive"]+=1
            else:
                results["False_Postive"]+=1
        results["False_Negative"] = len(set(stemmed_tags).difference(set(stemmed_keywords)))
        recall = results["True_Positive"]*1.0/len(stemmed_tags)
        precision = results["True_Positive"]*1.0 / results["True_Positive"]+results["False_Negative"]
        f_score = 2*(precision*recall)/(precision+recall)
        return pandas.Series({"recall":recall,"precision":precision,"f_score":f_score})
    
if __name__ == '__main__':
    articles = getXMLFeedAsListOfItems()
    writeArticlesDatToCSV(articles)
