from flask import render_template, request, redirect, url_for, Response
from . import view_blue
from public_index import *
from recommend import *
from search import search
import time

@view_blue.route('/result')
def result():
    t = time.perf_counter() # 计时
    keywords = request.args.get('keywords')
    if request.cookies.get('search_history'):
        search_history: list = json.loads(request.cookies.get('search_history'))
    else:
        search_history = []
    
    if not keywords:
        return redirect(url_for('view.home'))
    else:
        try:
            result_list = search(keywords, search_history)
            final_result = []
            for url, score in result_list: # 提取结果要显示的内容
                url_title = webpage.loc[url, 'title']
                url_date = webpage.loc[url, 'date']
                url_date = url_date.strftime('%Y-%m-%d %H:%M:%S')
                url_content = webpage.loc[url, 'content']
                url_description = ''
                if not pd.isna(url_content):
                    # 显示内容的前 140 个字为摘要
                    url_description = url_content[:(140 if 140 < len(url_content) else len(url_content)-1)] + '…'
                final_result.append((url_title, url, url_description, url_date, score))
            recommend_list = recommend(final_result, keywords)
        except KeyError:
            cost_t = f'{time.perf_counter()-t: .2f}'
            return render_template('no_result.html', keywords=keywords, cost_time=cost_t)
        cost_t = f'{time.perf_counter()-t: .2f}'

    if len(final_result)==0:
        return render_template('no_result.html', keywords=keywords, cost_time=cost_t)

    resp = Response(render_template('result.html', keywords=keywords, results=final_result, len_results=len(final_result), 
                                    cost_time=cost_t, search_history=search_history, recommend_list = recommend_list))
    # 更新检索历史
    if keywords not in search_history:
        search_history.append(keywords)
    if len(search_history) > 10:
        search_history.pop(0)

    resp.set_cookie('search_history', json.dumps(search_history), max_age=60*60*24*30)
    return resp