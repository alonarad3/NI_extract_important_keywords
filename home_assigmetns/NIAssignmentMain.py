from time import time
import warnings
warnings.filterwarnings("ignore") ## all warnings are not mine, needs neater solution
import pandas

from home_assigmetns.classFeedArticle import FeedArticle
from home_assigmetns import parsingUtils


csv_path = r"C:\Users\Alon Arad\Documents\NI\articles_dat_2.csv"

def runExtarctKeywordsOnFeedBurnerTC():
    articles =[]
    parsedXML = parsingUtils.parseXMLPage()
    for article in parsedXML.find_all("item"):
        article = FeedArticle(article)
        print "##############"
        print "##############"
        print "title : ",article.title
        print "-------------------"
        print "url link : ",article.url
        print "-------------------"
        print "important keywords : ",article.important_keywords 
        articles.append(article)
    return articles    
 
def writeArticlesDatToCSV(articles,csvPath = csv_path):
    articles_df = pandas.DataFrame([article.__dict__ for article in articles],columns=["article_id","url","title","article_content","tech_crunch_tags","word_phrase_to_ref_link","important_keywords","recall","precision","f_score"])
    try:
        with open(csvPath, 'a') as f:
            articles_df.to_csv(f, header=False)
    except:
        articles_df.to_csv(csvPath)




    
if __name__ == '__main__':
    runExtarctKeywordsOnFeedBurnerTC()
#     writeArticlesDatToCSV(articles)
