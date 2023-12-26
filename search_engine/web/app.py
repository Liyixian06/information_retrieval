from flask import Flask
from flask_bootstrap import Bootstrap5
from public_index import *
from views import view_blue

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.config["SECRET_KEY"] = '123456'

app.register_blueprint(view_blue)

if __name__ == '__main__':
    app.run()