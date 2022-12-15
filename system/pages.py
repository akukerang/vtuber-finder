from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import spacy
from collections import Counter

def onlyAlpha(c : str) -> bool:
    for _i in c:
        if str(_i).isdigit():
            return False
    return True

def tag_visible(element) -> bool: #Checks if the element is visible on the page
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def filterPage(soup: BeautifulSoup) -> None:  # Gets rid of unnecessary elements
    filterSections = ['toc', 'mw-references-wrap']
    filterElements = ['table', 'h1', 'h2', 'h3',
                    'h4', 'img', 'svg', 'sup', 'aside']
    for sections in filterSections:
        try:
            soup.find('div', class_=str(sections)).decompose()
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

def extractList(list: list) -> list:
    return [_i[0] for _i in list]

class pages:
    def __init__(self, name: str, numWords: int):
        self.name = name
        self.numWords = numWords
        r = requests.get(f"https://virtualyoutuber.fandom.com/wiki/{name}")
        self.content = r.content

    def getPageText(self) -> str:
        soup = BeautifulSoup(self.content, 'lxml')
        s = filterPage(soup)
        try:
            texts = s.findAll(text=True)
            visible_texts = filter(tag_visible, texts)
            pageText = " ".join(t.strip() for t in visible_texts)
            pageText = pageText.replace('\n', '')
        except:
            pass
        return pageText

    def getPageKeywords(self, nlp: spacy.language) -> list:
        if (self.name == ''):
            return []
        else:
            text = self.getPageText()
            doc = nlp(text)
            keys = Counter([ascii(t) for t in doc.ents if onlyAlpha(str(t)) and (str(
                t) != '' or str(t) != ' ')])  # filters out dates, numbers, newlines, empty strings
            # gets 50 most used keywords
            keywords = extractList(keys.most_common(self.numWords))
            keywords = [x.lower() for x in keywords]  # lowercases all strings
            return keywords

    def getPageSocials(self):
        soup = BeautifulSoup(self.content, 'lxml')
        socialTypes = ['twitter','twitch','youtube']
        socials = []
        try:
            section = soup.find('aside',class_='portable-infobox pi-background pi-border-color pi-theme-wikia pi-layout-default')
            try:
                socials.append(['image', section.find('img')['src']])
            except:
                pass #If there is no image provided, returns a NoneType Error
            try:
                for link in section.find_all('a'):
                    if link.has_attr('href') and str(link.contents[0]).lower() in socialTypes:
                        socials.append([str(link.contents[0]).lower(), link['href']])
            except:
                pass
        except:
            pass
        return socials
