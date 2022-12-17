import sys
from flask import Flask, render_template, request
sys.path.append('system/')
from recommendation import recommendSystem
import pandas as pd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'temp'
keywords: list = []
dataframe:list = []
r = recommendSystem('data/english_processed.csv')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sendkeywords')
def getKeywords():
    keywords = request.args.get('data')
    keywords = list(keywords.lower().split(","))
    keywords = [str(keyword).strip() for keyword in keywords]
    dataframe = r.keyword_recommend(keywords)
    return render_template('results.html',dataframe=dataframe, keywords=keywords)


app.run()

