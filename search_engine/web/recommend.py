import jieba.analyse
from public_index import *

def is_number(s):
    if s.isnumeric():
        return True
    else:
        try:
            float(s)
            return True
        except ValueError:
            return False

def recommend(results, keywords):
    split_keyword = list(jieba.cut_for_search(keywords))
    split_keyword.sort()
    if '' in split_keyword:
        split_keyword.remove('')
    if ' ' in split_keyword:
        split_keyword.remove(' ')

    extract_tags = {}
    for res in results[: (30 if len(results)>=30 else len(results))]:
        tmp_tags = jieba.analyse.extract_tags(webpage.loc[res[1],'title'], topK=3, withWeight=True)
        for word, weight in tmp_tags:
            if word not in extract_tags:
                extract_tags[word] = res[4]*weight
            else:
                extract_tags[word] += res[4]*weight
        content = webpage.loc[res[1],'content']
        if not pd.isna(content):
            tmp_tags = jieba.analyse.extract_tags(webpage.loc[res[1],'content'], topK=20, withWeight=True)
            for word, weight in tmp_tags:
                if word not in extract_tags:
                    extract_tags[word] = res[4]*weight*3
                else:
                    extract_tags[word] += res[4]*weight*3

    for word in split_keyword:
        if word in extract_tags.keys():
            del extract_tags[word]
    
    extract_tags_list = sorted(extract_tags.keys(), key=lambda d:extract_tags[d], reverse=True)
    for word in extract_tags.keys():
        if is_number(word):
            extract_tags_list.remove(word)

    return extract_tags_list[: (10 if len(extract_tags_list)>=10 else len(extract_tags_list))]