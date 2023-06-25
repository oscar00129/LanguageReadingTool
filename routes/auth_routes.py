from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
import mysql.connector
from configparser import ConfigParser
import json, helpers

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    logged_user = session.get('logged_user')
    if logged_user:
        return redirect(url_for('index'))
    else:
        language = helpers.readConfig('APP', 'LANGUAGE')
        data = helpers.getLanguageData(language)
        return render_template('login.html', data = data)

@auth_bp.route('/loginBackend', methods=['POST'])
def loginBackend():
    txtUser = request.get_json()['txtUser']
    txtPass = request.get_json()['txtPass']

    cn = mysql.connector.connect(
        host = helpers.readConfig('DATABASE', 'HOST'),
        port = helpers.readConfig('DATABASE', 'PORT', True),
        user = helpers.readConfig('DATABASE', 'USER'),
        password = helpers.readConfig('DATABASE', 'PASSWORD'),
        database = helpers.readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    # Consulta segura con parámetros de consulta
    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    params = (txtUser, txtPass)
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    cn.close()

    language = helpers.readConfig('APP', 'LANGUAGE')
    data = helpers.getLanguageData(language)
    if len(results) > 0:
        session['logged_user'] = txtUser
        return json.dumps({ 'success': data['language_data']['login_data']['messages']['login_success'] })
    else:
        return json.dumps({ 'error': data['language_data']['login_data']['messages']['error_credentials'] })

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
        language = helpers.readConfig('APP', 'LANGUAGE')
        data = helpers.getLanguageData(language)
        return render_template('register.html', data = data)

@auth_bp.route('/registerBackend', methods=['POST'])
def registerBackend():
    txtUser = request.get_json()['txtUser']
    txtPass = request.get_json()['txtPass']

    cn = mysql.connector.connect(
        host = helpers.readConfig('DATABASE', 'HOST'),
        port = helpers.readConfig('DATABASE', 'PORT', True),
        user = helpers.readConfig('DATABASE', 'USER'),
        password = helpers.readConfig('DATABASE', 'PASSWORD'),
        database = helpers.readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    # Comprobar email unico
    query = "SELECT * FROM users WHERE email = %s"
    params = (txtUser,)
    cursor.execute(query, params)
    results = cursor.fetchall()
    language = helpers.readConfig('APP', 'LANGUAGE')
    data = helpers.getLanguageData(language)
    if len(results) > 0:
        return json.dumps({ 'error': data['language_data']['register_data']['messages']['email_already_registered'] })
    
    # Registro
    query = "INSERT INTO users (email, password) VALUES (%s, %s);"
    params = (txtUser, txtPass)
    cursor.execute(query, params)
    cn.commit()
    if cursor.rowcount > 0:
        cursor.close()
        cn.close()
        # El registro fue exitoso
        return json.dumps({ 'success': data['language_data']['register_data']['messages']['email_registered_successfully'] })
    else:
        cursor.close()
        cn.close()
        # El registro falló
        return json.dumps({ 'error': data['language_data']['register_data']['messages']['problem'] })