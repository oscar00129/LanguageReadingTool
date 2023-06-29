from flask import Blueprint, render_template, request, session, redirect, url_for
import json, helpers

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    if helpers.getLoggedUser():
        return redirect(url_for('index'))
    else:
        data = helpers.getLanguageData()
        return render_template('login.html', data = data)

@auth_bp.route('/loginBackend', methods=['POST'])
def loginBackend():
    txtUser = request.get_json()['txtUser']
    txtPass = request.get_json()['txtPass']

    query = "SELECT * FROM users WHERE email = %s AND password = %s"
    params = (txtUser, txtPass)
    results = helpers.requestDB(query, params)

    data = helpers.getLanguageData()
    if len(results) > 0:
        logged_user_data = {}
        for result in results:
            logged_user_data = {
                'id': result[0],
                'email': result[1]
            }
        session['logged_user'] = logged_user_data
        return json.dumps({ 'success': data['language_data']['login_data']['messages']['login_success'] })
    else:
        return json.dumps({ 'error': data['language_data']['login_data']['messages']['error_credentials'] })

@auth_bp.route('/logout')
def logout():
    session.pop('logged_user', None)
    return redirect(url_for('index'))

@auth_bp.route('/register')
def register():
    if helpers.getLoggedUser():
        return redirect(url_for('index'))
    else:
        data = helpers.getLanguageData()
        return render_template('register.html', data = data)

@auth_bp.route('/registerBackend', methods=['POST'])
def registerBackend():
    txtUser = request.get_json()['txtUser']
    txtPass = request.get_json()['txtPass']

    # Comprobar email unico
    query = "SELECT * FROM users WHERE email = %s"
    params = (txtUser,)
    results = helpers.requestDB(query, params)
    data = helpers.getLanguageData()

    if len(results) > 0:
        return json.dumps({ 'error': data['language_data']['register_data']['messages']['email_already_registered'] })
    
    # Registro
    query = "INSERT INTO users (email, password) VALUES (%s, %s);"
    params = (txtUser, txtPass)
    result = helpers.requestDB(query, params)
    
    if type(result) == int:
        # El registro fue exitoso
        return json.dumps({ 'success': data['language_data']['register_data']['messages']['email_registered_successfully'] })
    else:
        # El registro falló
        return json.dumps({ 'error': data['language_data']['register_data']['messages']['problem'] })