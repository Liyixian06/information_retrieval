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
    """
    输入：本次搜索的结果、本次搜索的关键词（用于排除）
    输出：一个推荐词列表
    """

    split_keyword = list(jieba.cut_for_search(keywords))
    split_keyword.sort()
    if '' in split_keyword:
        split_keyword.remove('')
    if ' ' in split_keyword:
        split_keyword.remove(' ')

    # 对每篇本次搜索的结果文档提取 20 个关键词，合并、计算其权重，最后按权重排序推荐
    # 搜索结果已经是加入搜索历史的个性化结果了，不用再算一次
    extract_tags = {}
    for res in results[: (30 if len(results)>=30 else len(results))]: # 性能所限，这里只简单地取前 30 篇；稍微复杂的实现是根据文档的相似度筛选
        tmp_tags = jieba.analyse.extract_tags(webpage.loc[res[1],'title'], topK=3, withWeight=True)
        # 上面的提取会返回一个 [word, weight] 的列表
        for word, weight in tmp_tags:
            if word not in extract_tags:
                # 因为这里的 weight 是提取的关键词对所在文档的权重，还要乘以文档本身和 query 的相似度
                extract_tags[word] = res[4]*weight
            else:
                extract_tags[word] += res[4]*weight
        content = webpage.loc[res[1],'content']
        if not pd.isna(content):
            tmp_tags = jieba.analyse.extract_tags(content, topK=20, withWeight=True)
            for word, weight in tmp_tags:
                if word not in extract_tags:
                    extract_tags[word] = res[4]*weight
                else:
                    extract_tags[word] += res[4]*weight

    # 剔除搜索的关键词
    for word in split_keyword:
        if word in extract_tags.keys():
            del extract_tags[word]
    
    extract_tags_list = sorted(extract_tags.keys(), key=lambda d:extract_tags[d], reverse=True)
    # 去掉数字
    for word in extract_tags.keys():
        if is_number(word):
            extract_tags_list.remove(word)

    # 返回权重最高的前10个
    return extract_tags_list[: (10 if len(extract_tags_list)>=10 else len(extract_tags_list))]