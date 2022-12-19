import sys
from flask import Flask, render_template, request
sys.path.append('system/')
from recommendation import recommendSystem, concat_df
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sendkeywords')
def getKeywords():
    processed_keys=[]
    languages = request.args.get('languages')
    if languages == '':
        languages = ['english']
    else:        
        languages = list(languages.split(','))

    df = concat_df(languages)
    namelist = df['names'].tolist()
    r = recommendSystem(df)

    keywords = request.args.get('data')
    keywords = list(keywords.lower().split(","))
    keywords = [str(keyword).strip() for keyword in keywords]
    for i in keywords:
        if i in namelist:
            vtube = df.loc[df.names == i] 
            keys = vtube['keywords'].iloc[0].split(',') 
            processed_keys+=keys
        else:
            i = i.replace(' ','-')
            processed_keys.append(i)
    dataframe = r.keyword_recommend(processed_keys)
    dataframe = dataframe[dataframe['names'].isin(keywords) == False] #Drops row if there is a vtuber in keywords
    return render_template('results.html',dataframe=dataframe[:5], keywords=keywords,languages=languages)


app.run()





