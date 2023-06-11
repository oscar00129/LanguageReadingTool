from flask import Blueprint, render_template, request, session, redirect, url_for
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

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    logged_user = session.get('logged_user')
    if logged_user:
        return redirect(url_for('index'))
    else: 
        return render_template('login.html', error=error)

@auth_bp.route('/loginBackend', methods=['POST'])
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
        return redirect(url_for('auth.login', error=True))

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
        return render_template('register.html')

@auth_bp.route('/registerBackend', methods=['POST'])
def registerBackend():
    txtUser = request.get_json()['txtUser']
    txtPass = request.get_json()['txtPass']

    cn = mysql.connector.connect(
        host=readConfig('DATABASE', 'HOST'),
        port=readConfig('DATABASE', 'PORT', True),
        user=readConfig('DATABASE', 'USER'),
        password=readConfig('DATABASE', 'PASSWORD'),
        database=readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    # Comprobar email unico
    query = "SELECT * FROM users WHERE email = %s"
    params = (txtUser,)
    cursor.execute(query, params)
    results = cursor.fetchall()
    if len(results) > 0:
        return json.dumps({ 'error': 'Email is already registered.' })
    
    # Registro
    query = "INSERT INTO users (email, password) VALUES (%s, %s);"
    params = (txtUser, txtPass)
    cursor.execute(query, params)
    cn.commit()
    if cursor.rowcount > 0:
        cursor.close()
        cn.close()
        # El registro fue exitoso
        return json.dumps({ 'success': 'Email has been registered successfully.' })
    else:
        cursor.close()
        cn.close()
        # El registro falló
        return json.dumps({ 'error': 'There was a problem with request, try again later.' })