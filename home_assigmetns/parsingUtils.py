import BeautifulSoup
import requests


def parseXMLPage(pageUrl="http://feeds.feedburner.com/TechCrunch/"):
    pageResponse = requests.get(pageUrl, timeout=5)
    pageParsedContent = BeautifulSoup(pageResponse.content,"xml")
    return pageParsedContent

def _getTextElement(element):
    """ return if a parsed html element containes text that is related to the article"""
    if element.name == "p":
        return element.get_text()
    return  ""