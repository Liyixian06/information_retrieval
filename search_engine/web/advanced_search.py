from datetime import timedelta
import pandas as pd
from public_index import *

def advanced_search(form, url):
    """
    输入：高级检索选项的表格，一个网页链接
    输出：该网页是否满足高级检索选项
    """
    
    and_words = form.and_words.data
    or_words = form.or_words.data
    no_words = form.no_words.data
    site = form.site.data
    time = form.time.data
    is_title_only = True if form.title_only.data=='Title only' else False

    title = webpage.loc[url, 'title']
    date = webpage.loc[url, 'date']
    content = webpage.loc[url, 'content']
    if pd.isna(content):
        content = ''

    # 1. 包含全部词汇
    if and_words:
        and_words_list = and_words.split('AND')
        if '' in and_words_list:
            and_words_list.remove('')
        if ' ' in and_words_list:
            and_words_list.remove(' ')
        if is_title_only:
            for word in and_words_list:
                word = word.strip()
                if word not in title:
                    return False
        else:
            for word in and_words_list:
                word = word.strip()
                if word not in title and word not in content:
                    return False

    # 2. 包含任意词汇
    if or_words:
        or_words_list = or_words.split('OR')
        if '' in or_words_list:
            or_words_list.remove('')
        if ' ' in or_words_list:
            or_words_list.remove(' ')
        if is_title_only:
            for word in or_words_list:
                word = word.strip()
                if word in title:
                    return True
        else:
            for word in or_words_list:
                word = word.strip()
                if word in title or word in content:
                    return True
        return False

    # 3. 不包含词汇
    if no_words:
        no_words_list = no_words.split('-')
        if '' in no_words_list:
            no_words_list.remove('')
        if ' ' in no_words_list:
            no_words_list.remove(' ')
        for word in no_words_list:
            word = word.strip()
            if word in title or word in content:
                return False

    # 4. 网站或域名
    if site and (site not in url):
        return False
    
    # 5. 时间
    if time:
        date = date.to_pydatetime()
        now = datetime.now()
        if time == 'Within a day' and now - date > timedelta(days=1):
            return False
        elif time == 'Within a week' and now - date > timedelta(days=7):
            return False
        elif time == 'Within a month' and now - date > timedelta(days=30):
            return False
        elif time == 'Within a year' and now - date > timedelta(days=365):
            return False
    
    return True