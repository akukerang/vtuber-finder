# vtuber-finder
Vtuber Finder is a keyword recommendation system, that assists people in finding new vtubers to watch.
<p>
It does this through using a dataset of keywords that corresponds to a vtuber. These keywords are based off the top 100 most used words from their wiki page.
Then, the system attempts to find the top 5 vtuber with the most similar keywords, based off the vtubers and keywords the user provides.
</p>

## Usage
1. Install the required libraries through running `pip install -r requirements.txt` from the terminal.
2. Run `flask/home.py`, and go to the link returned.
3. Check the desired languages.
4. Enter keywords and/or vtubers into the input, that you wish to see more of like.
5. Press Submit
<br>
<br>
<img src = "images/vtubers.png" style ="width: 50%; ">
<br>
<img src = "images/keywords.png" style ="width: 50%; ">

## Creating more datasets
If you wish to create more datasets. In the terminal, run `python -m spacy download en_core_web_sm`, to install the keyword processor library. 
This example would create a dataset of 50 keywords for all English vtubers.
```
from system.getData import generateData
test = generateData('English',50,'english)
allPages = test.getAllPages()
test.createDataset(allPages)
test.processKeywords()
```


