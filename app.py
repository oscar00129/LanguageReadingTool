from flask import Flask, render_template, request, session, redirect, url_for
from janome.tokenizer import Tokenizer
import json
import mysql.connector
from configparser import ConfigParser

app = Flask(__name__)
app.secret_key = 'secret_key_example_language'

def readConfig(category, attribute, is_int = False):
    config = ConfigParser()
    config.read('config.ini')
    if is_int:
        return config.getint(category, attribute)
    else:
        return config[category][attribute]

@app.route('/')
def index():
    logged_user = session.get('logged_user')
    if logged_user:
        return render_template('index.html', logged_user=logged_user)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    logged_user = session.get('logged_user')
    if logged_user:
        return redirect(url_for('index'))
    else: 
        return render_template('login.html', error=error)

@app.route('/loginBackend', methods=['POST'])
def loginBackend():
    txtUser = request.form['txtUser']
    txtPass = request.form['txtPass']
    #cbRemember = request.form.get('cbRemember')

    cn = mysql.connector.connect(
        host=readConfig('DATABASE', 'HOST'),
        port=readConfig('DATABASE', 'PORT', True),
        user=readConfig('DATABASE', 'USER'),
        password=readConfig('DATABASE', 'PASSWORD'),
        database=readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    # Consulta segura con parámetros de consulta
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    params = (txtUser, txtPass)
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    cn.close()

    if len(results) > 0:
        session['logged_user'] = txtUser
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login', error=True))

@app.route('/logout')
def logout():
    session.pop('logged_user', None)
    return redirect(url_for('index'))

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
