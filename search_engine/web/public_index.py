from os.path import dirname, abspath
import json
import pandas as pd
from datetime import datetime

path = dirname(dirname(abspath(__file__)))

with open(path + '/freq/idf.json', 'r', encoding='utf-8') as f:
    idf = json.load(f)

with open(path + '/freq/tf-idf.json', 'r', encoding='utf-8') as f:
    tf_idf = json.load(f)

with open(path + '/freq/word_freq.json', 'r', encoding='utf-8') as f:
    word_freq = json.load(f)
    word_set = sorted(set(word_freq.keys()))

with open(path + '/freq/doc_len.json', 'r', encoding='utf-8') as f:
    doc_len = json.load(f)

with open(path + '/freq/idf_title.json', 'r', encoding='utf-8') as f:
    idf_title = json.load(f)

with open(path + '/freq/tf-idf_title.json', 'r', encoding='utf-8') as f:
    tf_idf_title = json.load(f)

with open(path + '/freq/word_freq_title.json', 'r', encoding='utf-8') as f:
    word_freq_title = json.load(f)
    word_set_title = sorted(set(word_freq_title.keys()))

with open(path + '/freq/doc_len_title.json', 'r', encoding='utf-8') as f:
    doc_len_title = json.load(f)

webpage = pd.read_csv(path + '/data/gcore_article.csv', encoding='gb18030', index_col=1, usecols=['url','title','date','content'],
                      parse_dates=['date'], date_parser=lambda x:datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
webpage.fillna('')
page_rank = pd.read_csv(path + '/data/page_rank.csv', index_col=0)