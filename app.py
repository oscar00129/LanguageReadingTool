from flask import Flask, render_template, request, session, redirect, url_for
from janome.tokenizer import Tokenizer
import json
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret_key_example_language'

@app.route('/')
def index():
    logged_user = session.get('logged_user')
    if logged_user:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loginBackend', methods=['POST'])
def loginBackend():
    txtUser = request.form['txtUser']
    txtPass = request.form['txtPass']
    #cbRemember = request.form.get('cbRemember')

    cn = mysql.connector.connect(
        host="127.0.0.1",
        port="3306",
        user="root",
        password="",
        database="language"
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
        # TODO: Add wrong login fuctions
        return redirect(url_for('login'))

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
