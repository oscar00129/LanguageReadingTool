from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import mysql.connector
from configparser import ConfigParser
import json

auth_bp = Blueprint('auth', __name__)

def readConfig(category, attribute, is_int = False):
    config = ConfigParser()
    config.read('config.ini')
    if is_int:
        return config.getint(category, attribute)
    else:
        return config[category][attribute]

def getLanguageData(language_config):
    with open('language_texts.json') as json_file:
        data = json.load(json_file)
        local_language_data = list(filter(lambda language: language['language'] == language_config, data['languages']))
        return local_language_data[0] or {}

@auth_bp.route('/login')
def login():
    logged_user = session.get('logged_user')
    if logged_user:
        return redirect(url_for('index'))
    else:
        language = readConfig('APP', 'LANGUAGE')
        data = getLanguageData(language)
        return render_template('login.html', data = data)

@auth_bp.route('/loginBackend', methods=['POST'])
def loginBackend():
    txtUser = request.get_json()['txtUser']
    txtPass = request.get_json()['txtPass']

    cn = mysql.connector.connect(
        host = readConfig('DATABASE', 'HOST'),
        port = readConfig('DATABASE', 'PORT', True),
        user = readConfig('DATABASE', 'USER'),
        password = readConfig('DATABASE', 'PASSWORD'),
        database = readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    # Consulta segura con parámetros de consulta
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    params = (txtUser, txtPass)
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    cn.close()

    language = readConfig('APP', 'LANGUAGE')
    data = getLanguageData(language)
    if len(results) > 0:
        session['logged_user'] = txtUser
        return json.dumps({ 'success': data['login_data']['messages']['login_success'] })
    else:
        return json.dumps({ 'error': data['login_data']['messages']['error_credentials'] })

@auth_bp.route('/logout')
def logout():
    session.pop('logged_user', None)
    return redirect(url_for('index'))

@auth_bp.route('/register')
def register():
    logged_user = session.get('logged_user')
    if logged_user:
        return redirect(url_for('index'))
    else:
        language = readConfig('APP', 'LANGUAGE')
        data = getLanguageData(language)
        return render_template('register.html', data = data)

@auth_bp.route('/registerBackend', methods=['POST'])
def registerBackend():
    txtUser = request.get_json()['txtUser']
    txtPass = request.get_json()['txtPass']

    cn = mysql.connector.connect(
        host = readConfig('DATABASE', 'HOST'),
        port = readConfig('DATABASE', 'PORT', True),
        user = readConfig('DATABASE', 'USER'),
        password = readConfig('DATABASE', 'PASSWORD'),
        database = readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    # Comprobar email unico
    query = "SELECT * FROM users WHERE email = %s"
    params = (txtUser,)
    cursor.execute(query, params)
    results = cursor.fetchall()
    language = readConfig('APP', 'LANGUAGE')
    data = getLanguageData(language)
    if len(results) > 0:
        return json.dumps({ 'error': data['register_data']['messages']['email_already_registered'] })
    
    # Registro
    query = "INSERT INTO users (email, password) VALUES (%s, %s);"
    params = (txtUser, txtPass)
    cursor.execute(query, params)
    cn.commit()
    if cursor.rowcount > 0:
        cursor.close()
        cn.close()
        # El registro fue exitoso
        return json.dumps({ 'success': data['register_data']['messages']['email_registered_successfully'] })
    else:
        cursor.close()
        cn.close()
        # El registro falló
        return json.dumps({ 'error': data['register_data']['messages']['problem'] })