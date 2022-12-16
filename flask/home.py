from flask import Flask, render_template
import sys
sys.path.append('system/')
from recommendation import recommendSystem

app = Flask(__name__)

keywords: list = []
r = recommendSystem('data/english_processed.csv')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/sendkeywords/<keywords>', methods = ['POST'])
def getKeywords(keywords):
    keywords = list(keywords.lower().split(","))
    keywords = [str(keyword).strip() for keyword in keywords]
    print(keywords)
    r.keyword_recommend(keywords)
    return('/')



app.run()

