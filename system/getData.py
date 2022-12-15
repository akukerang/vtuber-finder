import requests
import time
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import spacy
from collections import Counter
import pandas as pd
from tqdm import tqdm
from nltk.tokenize import word_tokenize
import string

def tag_visible(element) -> bool: #Checks if the element is visible on the page
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def onlyAlpha(c : str) -> bool:
    for _i in c:
        if str(_i).isdigit():
            return False
    return True
    
def filterList(keywords: list):
    filtered = [i for i in keywords if not '\\\\' in i]
    filtered = [i for i in filtered if not all(j in string.punctuation for j in i)]
    return filtered

def extractList(list: list) -> list:
    return [_i[0] for _i in list]

def filterPage(soup : BeautifulSoup) -> None: #Gets rid of unnecessary elements
    filterSections = ['toc','mw-references-wrap']
    filterElements = ['table','h1','h2','h3','h4','img','svg','sup','aside']
    for sections in filterSections:
        try:
            soup.find('div',class_=str(sections)).decompose()
        except:
            pass
    for _i in filterElements:
        try:
            for tag in soup.find_all(str(_i)):
                tag.decompose()
        except:
            pass
    filtered = soup.find("div", class_='mw-parser-output')
    return filtered


def cleanUpKeys(keywordList: list) -> list:
    elementList = [[', ',','],['\'', ''],['\"', ''],[' ','-']]
    keywords = [i.lstrip('[') for i in keywordList]
    keywords = [i.rstrip(']') for i in keywords]
    for i, j in elementList:
        keywords = [k.replace(i,j) for k in keywords]
    keywords = [i.strip('-') for i in keywords]
    keywords = [word_tokenize(keyword.lower()) for keyword in keywords]
    keywords = [filterList(i) for i in keywords]
    return keywords


class generateData:
    def __init__(self, category="English" , numWords=50, filename='keywords'):
        self.category = category
        self.numWords = numWords
        self.filename = filename

    def getAllPages(self) -> list: #Generates a list of all pages for that category member
        allPages = []
        URLSTART = f"https://virtualyoutuber.fandom.com/api.php?action=query&format=json&list=categorymembers&formatversion=2&cmtitle=Category:{self.category}&cmlimit=500&cmsort=sortkey&cmdir=ascending"
        r = requests.get(URLSTART)
        data = r.json()
        cmcontinue = data['continue']['cmcontinue'] #Gets the starting location of the next items in the list
        for _i in data['query']['categorymembers']:
            allPages.append(_i['title'])
        while(True):
            URLTEMP = "https://virtualyoutuber.fandom.com/api.php?action=query&format=json&list=categorymembers&formatversion=2&cmtitle=Category:English&cmlimit=500&cmsort=sortkey&cmdir=ascending"
            r = requests.get(URLTEMP, params={'cmcontinue' : cmcontinue})
            data = r.json()
            for _i in data['query']['categorymembers']:
                allPages.append(_i['title'])
            try: 
                cmcontinue = data['continue']['cmcontinue'] #if cmcontinue does not exist, means at the end of the list
            except KeyError:
                for _i in data['query']['categorymembers']:
                    allPages.append(_i['title'])
                break
            time.sleep(5) #Delay for API calls
        return list(set(allPages)) 

    def getPageText(self, name: str) -> str:
        URL = f"https://virtualyoutuber.fandom.com/wiki/{name}"
        pageText = ""
        r = requests.get(URL)
        soup = BeautifulSoup(r.content, 'lxml') 
        s = filterPage(soup)
        try:
            texts = s.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            pageText = " ".join(t.strip() for t in visible_texts)
            pageText = pageText.replace('\n','')  
        except:
            pass
        return pageText

    def getPageKeywords(self, nlp : spacy.language, name: str) -> list:
        if(name == ''):
            return []
        else:
            text = self.getPageText(name)
            doc = nlp(text)
            keys = Counter([ascii(t) for t in doc.ents if onlyAlpha(str(t)) and (str(t) != '' or str(t) != ' ')]) #filters out dates, numbers, newlines, empty strings
            keywords = extractList(keys.most_common(self.numWords)) #gets 50 most used keywords
            keywords = [x.lower() for x in keywords] #lowercases all strings
            return keywords

    def createDataset(self, pages: list) -> None:
        nlp = spacy.load("en_core_web_sm")
        keywords = []
        for i in tqdm(pages):
            keyword = self.getPageKeywords(nlp, i)
            keywords.append(keyword)
            time.sleep(3.5) #Don't want to get rate limited :D
        df = pd.DataFrame({
            'names': pages,
            'keywords' : keywords
        })
        df.to_csv(f'data/{self.filename}.csv',mode='a',index=False)

    def processKeywords(self) -> None:
        df = pd.read_csv(f'data/{self.filename}.csv')
        keywords = df['keywords'].tolist()
        keywords = cleanUpKeys(keywords)
        df = pd.DataFrame({
            'names': df['names'].values,
            'keywords': keywords
        })
        df['keywords'] = df["keywords"].apply(lambda x: ",".join(map(str, x))).replace("", "none")
        df = df[df.keywords.values != "none"] #Gets rid of rows with no keywords
        df.to_csv(f'data/{self.filename}_processed.csv')

g = generateData('English',100,'english')
pages = g.getAllPages()
g.createDataset()
g.processKeywords()