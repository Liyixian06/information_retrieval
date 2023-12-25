from flask import render_template, request
from . import view_blue
import json

@view_blue.route('/')
def home():
    if request.cookies.get('search_history'):
        search_history: list = json.loads(request.cookies.get('search_history'))
    else:
        search_history = []
    return render_template('home.html', search_history = search_history)