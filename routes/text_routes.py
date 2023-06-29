from flask import Blueprint, session, render_template, redirect, url_for, request
import helpers, mysql.connector, json, nagisa

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
        logged_user_id = data['logged_user']['id']
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
        data['texts'] = serializable_results
        
        return render_template('texts.html', data = data)
    else:
        return redirect(url_for('auth.login'))
    
@text_bp.route('/texts/<int:text_id>')
def get_text(text_id):
    logged_user = session.get('logged_user')
    if logged_user:
        # Get language data
        language = helpers.readConfig('APP', 'LANGUAGE')
        data = helpers.getLanguageData(language)

        # Put logged user info
        data['logged_user'] = logged_user

        return render_template('text.html', data = data)
    else:
        return redirect(url_for('auth.login'))

@text_bp.route('/texts/getTextAndWords', methods=['POST'])
def get_text_and_words():
    # Get language data
    language = helpers.readConfig('APP', 'LANGUAGE')
    data = helpers.getLanguageData(language)

    logged_user = session.get('logged_user')
    text_id = request.get_json()['textId']
    text = json.loads(get_text_from_backend(logged_user, text_id))
    knowed_words = json.loads(get_knowed_words(logged_user))

    if text and text.get('error'):
        return json.dumps({ 'error': data['language_data']['text_data']['messages']['error'] })
    else:
        new_words = []
        for word in text['text']['text']:
            new_word = {
                'id': None,
                'user_id': logged_user['id'],
                'word': word,
                'status': 'unknown'
            }
            for knowed_word in knowed_words['knowed_words']:
                if word == knowed_word['word']:
                    new_word = {
                        'id': knowed_word['id'],
                        'user_id': logged_user['id'],
                        'word': knowed_word['word'],
                        'status': knowed_word['status']
                    }
            new_words.append(new_word)
        text['text']['text'] = new_words
        return json.dumps({ 'text': text })


# TODO: Add pagination functions
def get_text_from_backend(logged_user, text_id):
    # Get language data
    language = helpers.readConfig('APP', 'LANGUAGE')
    data = helpers.getLanguageData(language)

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
    params = (text_id, logged_user['id'])
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
            'text': nagisa.tagging(result[4]).words,
            'author_id': result[5],
            'is_public': result[6]
        }
    if len(results) > 0:
        return json.dumps({ 'text': result })
    else:
        return json.dumps({ 'error': data['language_data']['text_data']['messages']['error'] })

def get_knowed_words(logged_user):
    # Get knowed words
    cn = mysql.connector.connect(
        host = helpers.readConfig('DATABASE', 'HOST'),
        port = helpers.readConfig('DATABASE', 'PORT', True),
        user = helpers.readConfig('DATABASE', 'USER'),
        password = helpers.readConfig('DATABASE', 'PASSWORD'),
        database = helpers.readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    # Consulta segura con parámetros de consulta
    query = "SELECT * FROM words WHERE user_id = %s"
    params = (logged_user['id'],)
    cursor.execute(query, params)
    results = cursor.fetchall()
    cursor.close()
    cn.close()
    knowed_results = []
    for result in results:
        knowed_results.append({
            "id": result[0],
            "user_id": result[1],
            "word": result[2],
            "status": result[3]
        })
    return json.dumps({ 'knowed_words': knowed_results })

@text_bp.route('/texts/setStatus', methods=['POST'])
def set_status():
    # Get language data
    language = helpers.readConfig('APP', 'LANGUAGE')
    data = helpers.getLanguageData(language)

    word = request.get_json()['word']
    stats = request.get_json()['stats']
    text_id = request.get_json()['textId']

    logged_user = session.get('logged_user')
    if logged_user:
        # Get knowed words
        cn = mysql.connector.connect(
            host = helpers.readConfig('DATABASE', 'HOST'),
            port = helpers.readConfig('DATABASE', 'PORT', True),
            user = helpers.readConfig('DATABASE', 'USER'),
            password = helpers.readConfig('DATABASE', 'PASSWORD'),
            database = helpers.readConfig('DATABASE', 'DATABASE')
        )
        cursor = cn.cursor()
        # Consulta segura con parámetros de consulta
        query = "SELECT * FROM words WHERE user_id = %s AND word = %s"
        params = (logged_user['id'], word['word'])
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()

        if len(results) > 0:
            # Si ya hay un resultado solo actualizar el dato
            cursor = cn.cursor()
            
            # Si es a unknown, eliminar el registro, sino, actualizarlo
            if word['status'] == 'unknown':
                query = "DELETE FROM words WHERE id = %s"
                params = (results[0][0], )
                cursor.execute(query, params)
                cn.commit()
            else:
                query = "UPDATE words SET status = %s WHERE id = %s"
                params = (word['status'], results[0][0])
                cursor.execute(query, params)
                cn.commit()

            cursor.close()
        else:
            # Si no hay resultados, crear el registro
            cursor = cn.cursor()
            query = "INSERT INTO words (user_id, word, status) VALUES (%s, %s, %s)"
            params = (logged_user['id'], word['word'], word['status'])
            cursor.execute(query, params)
            cn.commit()
            cursor.close()

        # Actualizar los stats del texto
        cursor = cn.cursor()
        query = "UPDATE texts SET stats = %s WHERE id = %s"
        params = (stats, text_id)
        cursor.execute(query, params)
        cn.commit()
        cursor.close()

        print(stats)
        print(text_id)

        cn.close()
        return json.dumps({ 'success': data['language_data']['text_data']['messages']['success'] })
    else:
        return json.dumps({ 'error': data['language_data']['text_data']['messages']['error'] })

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
        return redirect(url_for('auth.login'))

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