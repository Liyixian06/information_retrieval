from flask import render_template, request, Response
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, RadioField, SubmitField
from wtforms.validators import DataRequired
from . import view_blue
from public_index import *
from recommend import *
from search import search
from advanced_search import advanced_search
import time

class AdvancedForm(FlaskForm):
    search_words = StringField('Search: ', validators=[DataRequired()])
    and_words = StringField('Include all(exact match): ')
    or_words = StringField('Include any(exact match): ')
    no_words = StringField('Not include: ')
    site = StringField('Site / Domain: ')
    time = SelectField('Updated time: ', choices=['Any','Within a day','Within a week', 'Within a month', 'Within a year'], validators=[DataRequired()])
    title_only = RadioField('Place: ', choices=['Full text', 'Title only'], validators=[DataRequired()])
    submit = SubmitField('Advanced Search')

@view_blue.route('/advanced', methods=['GET','POST'])
def advanced():
    form = AdvancedForm(time='Any', title_only='Full text')
    if request.method == 'GET':
        if request.args.get('keywords'):
            form.search_words.data = request.args.get('keywords')
    
    if form.validate_on_submit():
        t = time.perf_counter()
        if request.cookies.get('search_history'):
            search_history: list = json.loads(request.cookies.get('search_history'))
        else:
            search_history = []
        
        search_words = form.search_words.data
        if form.title_only.data == 'Title only':
            is_title_only = True
        else:
            is_title_only = False
        try:
            result_list = search(search_words, search_history, is_title_only)
            final_result = []
            for url, score in result_list:
                url_title = webpage.loc[url, 'title']
                url_date = webpage.loc[url, 'date']
                url_date = url_date.strftime('%Y-%m-%d %H:%M:%S')
                url_content = webpage.loc[url, 'content']
                url_description = ''
                if pd.isna(url_content) is False:
                    url_description = url_content[:(140 if 140 < len(url_content) else len(url_content)-1)] + '…'
                final_result.append((url_title, url, url_description, url_date, score))
            recommend_list = recommend(final_result, search_words)
        except KeyError:
            cost_t = f'{time.perf_counter()-t: .2f}'
            return render_template('no_result.html', keywords=search_words, cost_time=cost_t)
        
        filter_list = []
        for res in final_result:
            filter_list.append(advanced_search(form, res[1]))
        final_result = [res for res in final_result if res[1] not in filter_list]

        cost_t = f'{time.perf_counter()-t: .2f}'
        if len(final_result)==0:
            return render_template('no_result.html', keywords=search_words, cost_time=cost_t)
    
        resp = Response(render_template('result.html', keywords=search_words, results=final_result, len_results=len(final_result), 
                                    cost_time=cost_t, search_history=search_history, recommend_list=recommend_list))
        if search_words not in search_history:
            search_history.append(search_words)
        if len(search_history) > 10:
            search_history.pop(0)

        resp.set_cookie('search_history', json.dumps(search_history), max_age=60*60*24*30)
        return resp

    return render_template('advanced.html', form=form)