from datetime import timedelta
from public_index import *

def advanced_search(form, url):
    and_words = form.and_words.data
    or_words = form.or_words.data
    no_words = form.no_words.data
    site = form.site.data
    time = form.time.data
    is_title_only = True if form.title_only.data=='Title only' else False

    title = webpage.loc[url, 'title']
    date = webpage.loc[url, 'date']
    content = webpage.loc[url, 'content']

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
                    return url
        else:
            for word in and_words_list:
                word = word.strip()
                if word not in title and word not in content:
                    return url

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
                    return ''
        else:
            for word in or_words_list:
                word = word.strip()
                if word in title or word in content:
                    return ''
        return url

    if no_words:
        no_words_list = no_words.split('-')
        if '' in no_words_list:
            no_words_list.remove('')
        if ' ' in no_words_list:
            no_words_list.remove(' ')
        for word in no_words_list:
            word = word.strip()
            if word in title or word in content:
                return url

    if site and (site not in url):
        return url
    
    if time:
        date = date.to_pydatetime()
        now = datetime.now()
        if time == 'Within a day' and now - date > timedelta(days=1):
            return url
        elif time == 'Within a week' and now - date > timedelta(days=7):
            return url
        elif time == 'Within a month' and now - date > timedelta(days=30):
            return url
        elif time == 'Within a year' and now - date > timedelta(days=365):
            return url
    
    return ''