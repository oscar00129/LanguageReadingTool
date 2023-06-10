from flask import Flask, render_template, request, session, redirect, url_for
from janome.tokenizer import Tokenizer
import json
from routes import auth_routes

app = Flask(__name__)
app.secret_key = 'secret_key_example_language'

app.register_blueprint(auth_routes.auth_bp)

@app.route('/')
def index():
    logged_user = session.get('logged_user')
    if logged_user:
        return render_template('index.html', logged_user=logged_user)
    else:
        return redirect(url_for('auth.login'))

@app.route('/process', methods=['POST'])
def process():
    text = request.get_json()['text']
    #text = request.form['text']
    tokenizer = Tokenizer()
    words = [token.surface for token in tokenizer.tokenize(text)]
    #words = list(set(words))
    
    # Utilizamos la función map() para reemplazar " \n" por "\n" en cada palabra
    words = list(map(lambda word: "\n" if word == " \n" or word == "\u3000" else word, words))

    # Recorremos la lista y eliminamos un elemento si hay dos "\n" seguidos
    i = 0
    while i < len(words) - 1:
        if words[i] == "\n" and words[i+1] == "\n":
            words.pop(i)
        elif words[i] == " ":
            words.pop(i)
        else:
            i += 1

    print(words)

    return json.dumps({ 'data': { 'words': words } })

if __name__ == '__main__':
    app.run(debug=True)
