from flask import Blueprint, session, render_template, redirect, url_for, request
import helpers, mysql.connector, json

text_bp = Blueprint('text', __name__)

@text_bp.route('/texts')
def get_texts():
    logged_user = session.get('logged_user')
    if logged_user:
        # Get language data
        language = helpers.readConfig('APP', 'LANGUAGE')
        data = helpers.getLanguageData(language)

        # Put logged user info
        data['logged_user'] = logged_user

        # Get logged user texts
        logged_user_id = 5 # TODO: Change login params, add id
        cn = mysql.connector.connect(
            host = helpers.readConfig('DATABASE', 'HOST'),
            port = helpers.readConfig('DATABASE', 'PORT', True),
            user = helpers.readConfig('DATABASE', 'USER'),
            password = helpers.readConfig('DATABASE', 'PASSWORD'),
            database = helpers.readConfig('DATABASE', 'DATABASE')
        )
        cursor = cn.cursor()
        # Consulta segura con parámetros de consulta
        query = "SELECT * FROM texts WHERE author_id = %s"
        params = (logged_user_id,)
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        cn.close()
        serializable_results = []
        for result in results:
            serializable_result = {
                'id': result[0],
                'title': result[1],
                'img_src': result[2],
                'stats': json.loads(result[3].decode('utf-8')),
                'text': result[4],
                'author_id': result[5],
                'is_public': result[6]
            }
            serializable_results.append(serializable_result)
        data['texts'] = serializable_results # TODO: divide language json, add a key to languages
        
        return render_template('texts.html', data = data)
    else:
        return redirect(url_for('login'))
    
@text_bp.route('/texts/<int:text_id>')
def get_text(text_id):
    logged_user = session.get('logged_user')
    if logged_user:
        # Get language data
        language = helpers.readConfig('APP', 'LANGUAGE')
        data = helpers.getLanguageData(language)

        # Put logged user info
        data['logged_user'] = logged_user

        # Get logged user texts
        logged_user_id = 5 # TODO: Change login params, add id
        cn = mysql.connector.connect(
            host = helpers.readConfig('DATABASE', 'HOST'),
            port = helpers.readConfig('DATABASE', 'PORT', True),
            user = helpers.readConfig('DATABASE', 'USER'),
            password = helpers.readConfig('DATABASE', 'PASSWORD'),
            database = helpers.readConfig('DATABASE', 'DATABASE')
        )
        cursor = cn.cursor()
        # Consulta segura con parámetros de consulta
        query = "SELECT * FROM texts WHERE id = %s AND author_id = %s"
        params = (text_id, logged_user_id)
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        cn.close()

        result = {}
        for result in results:
            result = {
                'id': result[0],
                'title': result[1],
                'img_src': result[2],
                'stats': json.loads(result[3].decode('utf-8')),
                'text': result[4],
                'author_id': result[5],
                'is_public': result[6]
            }
        data['text'] = result # TODO: divide language json, add a key to languages
        
        return render_template('text.html', data = data)
    else:
        return redirect(url_for('login'))

@text_bp.route('/texts/add')
def add_text():
    logged_user = session.get('logged_user')
    if logged_user:
        # Get language data
        language = helpers.readConfig('APP', 'LANGUAGE')
        data = helpers.getLanguageData(language)

        # Put logged user info
        data['logged_user'] = logged_user

        return render_template('add.html', data = data)
    else:
        return redirect(url_for('login'))

@text_bp.route('/texts/addTextBackend', methods=['POST'])
def add_text_backend():
    language = helpers.readConfig('APP', 'LANGUAGE')
    data = helpers.getLanguageData(language)

    title = request.get_json()['title']
    img_src = request.get_json()['img_src']
    stats = request.get_json()['stats']
    text = request.get_json()['text']
    author_id = request.get_json()['author_id']
    is_public = request.get_json()['is_public']

    cn = mysql.connector.connect(
        host = helpers.readConfig('DATABASE', 'HOST'),
        port = helpers.readConfig('DATABASE', 'PORT', True),
        user = helpers.readConfig('DATABASE', 'USER'),
        password = helpers.readConfig('DATABASE', 'PASSWORD'),
        database = helpers.readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    
    # Registro
    query = "INSERT INTO texts (title, img_src, stats, text, author_id, is_public) VALUES (%s, %s, %s, %s, %s, %s);"
    params = (title, img_src, stats, text, author_id, is_public)
    cursor.execute(query, params)
    cn.commit()
    if cursor.rowcount > 0:
        cursor.close()
        cn.close()
        # El registro fue exitoso
        return json.dumps({ 'success': data['language_data']['text_data']['messages']['success'] })
    else:
        cursor.close()
        cn.close()
        # El registro falló
        return json.dumps({ 'error': data['language_data']['text_data']['messages']['error'] })