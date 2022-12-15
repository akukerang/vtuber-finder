from gensim.corpora.dictionary import Dictionary
from gensim.models.tfidfmodel import TfidfModel
from gensim.similarities import MatrixSimilarity
import pandas as pd
from nltk.tokenize import word_tokenize

def no_commas(doc: list) -> list:
    no_commas = [t for t in doc if t!=',']
    return(no_commas)


class recommendSystem:
    def __init__(self, filename:str):
        self.dataset = pd.read_csv(filename)
        keywords = self.dataset['keywords'].tolist()
        keywords = [word_tokenize(keyword.lower()) for keyword in keywords]
        keywords = [no_commas(kw) for kw in keywords]
        processed_keywords = keywords
        self.dictionary = Dictionary(processed_keywords) # create a dictionary of words from our keywords
        self.corpus = [self.dictionary.doc2bow(doc) for doc in processed_keywords] 
        self.tfidf = TfidfModel(self.corpus) #create tfidf model of the corpus
        self.sims = MatrixSimilarity(self.tfidf[self.corpus], num_features=len(self.dictionary))


    def vtuber_recommend(self, name:str, number_of_hits:int=5) -> None:
        vtube = self.dataset.loc[self.dataset.names==name] 
        keywords = vtube['keywords'].iloc[0].split(',') 
        query_doc = keywords 
        query_doc_bow = self.dictionary.doc2bow(query_doc) 
        query_doc_tfidf = self.tfidf[query_doc_bow] 
        similarity_array = self.sims[query_doc_tfidf] 
        similarity_series = pd.Series(similarity_array.tolist(), index=self.dataset.names) 
        top_hits = similarity_series.sort_values(ascending=False)[1:number_of_hits+1] 
        sorted_tfidf_weights = sorted(self.tfidf[self.corpus[vtube.index.values.tolist()[0]]], key=lambda w: w[1], reverse=True)
        print(top_hits)

