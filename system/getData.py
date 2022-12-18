import requests
import time
import requests
import spacy
import pandas as pd
from tqdm import tqdm
from nltk.tokenize import word_tokenize
import string
from pages import pages
import re
import ast
    
def filterList(keywords: list):
    filtered = [i for i in keywords if not '\\\\' in i]
    filtered = [i for i in filtered if not all(j in string.punctuation for j in i)]
    for punct in list(string.punctuation):
        filtered = [i.strip(punct) for i in filtered]
    filtered = list(dict.fromkeys(filtered))
    return filtered

def cleanUpKeys(keywordList: list) -> list:
    elementList = [[', ',','],['\'', ''],['\"', ''],[' ','-']]
    keywords = [i.lstrip('[') for i in keywordList]
    keywords = [i.rstrip(']') for i in keywords]
    for i, j in elementList:
        keywords = [k.replace(i,j) for k in keywords]
    keywords = [i.strip('-') for i in keywords]
    keywords = [word_tokenize(keyword.lower()) for keyword in keywords]
    keywords = [filterList(keyword) for keyword in keywords]

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

    def createDataset(self, pagesList: list) -> None:
        nlp = spacy.load("en_core_web_sm")
        keywords = []
        socials = []
        for page in tqdm(pagesList):
            current = pages(page, self.numWords)
            keyword = current.getPageKeywords(nlp)
            social = current.getPageSocials()
            keywords.append(keyword)
            socials.append(social)
            time.sleep(3.5) #Don't want to get rate limited :D
        df = pd.DataFrame({
            'names': pagesList,
            'keywords' : keywords,
            'socials' : socials
        })
        df.to_csv(f'data/{self.filename}.csv',mode='a',index=False)

    def processKeywords(self) -> None:
        df = pd.read_csv(f'data/{self.filename}.csv')
        keywords = df['keywords'].tolist()
        keywords = cleanUpKeys(keywords)
        df['names'] = df['names'].str.replace(r'User:.*?/', '', regex=True)
        socials = df['socials'].tolist()
        socials = [ast.literal_eval(i) for i in socials]
        df2 = pd.DataFrame(columns=['names','image','youtube','twitter','twitch'])
        for row in socials:
            data = {}
            for col in row:
                data[col[0]] = col[1]
            df2 = df2.append(data, ignore_index=True)
         #removes certain part from image url to allow it to display on webpage
        df2['image'] = df2['image'].str.replace(r"/revision/latest/scale-to-width-down/\d+\?cb=\d+", '', regex=True)
        df2['image'] = df2['image'].str.replace(r"/revision/latest\?cb=[^/]+", '', regex=True)

        df = pd.DataFrame({
            'names': df['names'].str.lower(),
            'keywords': keywords,
            'images': df2['image'].values,
            'twitter': df2['twitter'].values,
            'youtube': df2['youtube'].values,
            'twitch': df2['twitch'].values,
        })
        df['keywords'] = df["keywords"].apply(lambda x: ",".join(map(str, x))).replace("", "none")
        df = df[df.keywords.values != "none"] #Gets rid of rows with no keywords
        df.to_csv(f'data/{self.filename}_processed.csv')


g = generateData('English',100,'english')
g.processKeywords()
