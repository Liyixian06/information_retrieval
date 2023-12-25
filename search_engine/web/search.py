import jieba
import math
from public_index import *

def search(input_keyword: str, search_history: str, is_title_only: bool = False):
    
    if not is_title_only:
        util_word_set = word_set
        util_idf = idf
        util_tf_idf = tf_idf
        util_doc_len = doc_len
    else:
        util_word_set = word_set_title
        util_idf = idf_title
        util_tf_idf = tf_idf_title
        util_doc_len = doc_len_title
    
    split_keyword = list(jieba.cut_for_search(input_keyword))
    split_keyword.sort()
    if '' in split_keyword:
        split_keyword.remove('')
    if ' ' in split_keyword:
        split_keyword.remove(' ')
    
    split_history = []
    for history in search_history:
        tmp_split = list(jieba.cut_for_search(history))
        for word in tmp_split:
            if word is not '' and word is not ' ' and word not in split_history:
                split_history.append(word)
    
    input_tf_idf = {}
    for word in split_keyword:
        if word in util_word_set:
            freq = split_keyword.count(word)
            word_tf = 1 + math.log2(freq)
            input_tf_idf[word] = word_tf * util_idf[word]
        else:
            input_tf_idf[word] = 0
    
    history_tf_idf = {}
    for word in split_history:
        if word in util_word_set:
            freq = split_history.count(word)
            word_tf = 1 + math.log2(freq)
            history_tf_idf[word] = word_tf * util_idf[word]
        else:
            history_tf_idf[word] = 0
    
    url_sim = {}
    for url, tf_idf_dict in util_tf_idf.items():
        sim = 0
        for word, word_tf_idf in input_tf_idf.items():
            if word in tf_idf_dict:
                sim += word_tf_idf * tf_idf_dict[word]
        for word, word_tf_idf in history_tf_idf.items():
            if word in tf_idf_dict:
                sim += word_tf_idf * tf_idf_dict[word] * 0.03
        sim /= util_doc_len[url]
        if url in page_rank.index:
            sim = 2*(sim * page_rank.loc[url, 'page_rank']) / (sim + page_rank.loc[url, 'page_rank'])
        else:
            sim = 2*sim / (sim + 1)
        url_sim[url] = sim
    url_sim = sorted(url_sim.items(), key= lambda d:d[1], reverse=True)
    url_sim = [(u,s) for u, s in url_sim if s!=0.0]

    return url_sim