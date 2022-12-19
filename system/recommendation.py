from gensim.corpora.dictionary import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.similarities import MatrixSimilarity
import pandas as pd
from nltk.tokenize import word_tokenize

def no_commas(doc: list) -> list:
    no_commas = [t for t in doc if t!=',']
    return(no_commas)


def concat_df(languages: list) -> pd.DataFrame:
    df = pd.DataFrame(columns=["names","keywords","images","twitter","youtube"])
    for i in languages:
        df = pd.concat([df, pd.read_csv(f'data/{i}_processed.csv')], ignore_index=True).drop_duplicates()
    return df
    


class recommendSystem:
    def __init__(self, df:pd.DataFrame):
        self.dataset = df
        keywords = self.dataset['keywords'].tolist()
        keywords = [word_tokenize(keyword.lower()) for keyword in keywords]
        keywords = [no_commas(kw) for kw in keywords]
        processed_keywords = keywords
        self.dictionary = Dictionary(processed_keywords) # create a dictionary of words from our keywords
        self.corpus = [self.dictionary.doc2bow(doc) for doc in processed_keywords] 
        self.tfidf = TfidfModel(self.corpus) #create tfidf model of the corpus
        self.sims = MatrixSimilarity(self.tfidf[self.corpus], num_features=len(self.dictionary))

    def keyword_recommend(self, keywords: list) -> None:
        query_doc_bow = self.dictionary.doc2bow(keywords) 
        query_doc_tfidf = self.tfidf[query_doc_bow] 
        similarity_array = self.sims[query_doc_tfidf] 
        similarity_df = pd.DataFrame({
            'names' : self.dataset.names,
            'similarity' : similarity_array.tolist(),
            'images': self.dataset.images,
            'twitter': self.dataset.twitter,
            'youtube': self.dataset.youtube,
            'twitch': self.dataset.twitch
        })
        return similarity_df.sort_values(by=['similarity'], ascending=False)

