import jieba
import math
from public_index import *


def search(input_keyword: str, search_history: str, is_title_only: bool = False):
    """
    输入：本次搜索的关键词、搜索历史（个性化检索）、是否只检索标题
    输出：一个 (url, similarity) 列表，按相似度排序
    """

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
    
    # 关键词和搜索历史分词
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
    
    # 计算关键词和搜索历史的 tf-idf 值
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
    
    # 计算和每篇文档的余弦相似度
    url_sim = {}
    for url, tf_idf_dict in util_tf_idf.items():
        sim = 0
        for word, word_tf_idf in input_tf_idf.items():
            if word in tf_idf_dict:
                sim += word_tf_idf * tf_idf_dict[word]
        # 此处必须先判断是否为零
        # 如果不判断就添加搜索历史的权重，就会出现一种情况：某个页面和搜索关键词的相似度为零，但包含了某些搜索历史，它也会出现在结果里，但用户并不需要
        if sim!=0:
            for word, word_tf_idf in history_tf_idf.items():
                if word in tf_idf_dict:
                    sim += word_tf_idf * tf_idf_dict[word] * 0.03
        sim /= util_doc_len[url] # 先前已经计算过的文档向量长度直接拿来用
        # 余弦相似度和 pagerank 取调和平均
        if url in page_rank.index:
            sim = 2*(sim * page_rank.loc[url, 'page_rank']) / (sim + page_rank.loc[url, 'page_rank'])
        else:
            sim = 2*sim / (sim + 1)
        url_sim[url] = sim
    url_sim = sorted(url_sim.items(), key= lambda d:d[1], reverse=True)
    # 这里只剔除了相似度为零的，也可以筛选相似度必须大于某个最小值
    url_sim = [(u,s) for u, s in url_sim if s!=0.0]

    return url_sim