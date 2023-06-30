from flask import Flask, render_template, request, session, redirect, url_for
from janome.tokenizer import Tokenizer
import json, nagisa
from routes import auth_routes
from routes import text_routes
import helpers

app = Flask(__name__)
app.secret_key = 'secret_key_example_language'

app.register_blueprint(auth_routes.auth_bp)
app.register_blueprint(text_routes.text_bp)

@app.route('/')
def index():
    if helpers.getLoggedUser():
        return redirect(url_for('text.get_texts'))
    else:
        return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
