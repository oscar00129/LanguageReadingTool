from flask import Blueprint, render_template, redirect, url_for, request
import helpers, json, nagisa

text_bp = Blueprint('text', __name__)

@text_bp.route('/texts')
def get_texts():
    logged_user = helpers.getLoggedUser()
    if logged_user:
        # Get language data
        data = helpers.getLanguageData()
        # Put logged user info
        data['logged_user'] = logged_user
        return render_template('texts.html', data = data)
    else:
        return redirect(url_for('auth.login'))

@text_bp.route('/texts/getTextsAndWords')
def get_texts_and_words():
    logged_user = helpers.getLoggedUser()
    # Get language data
    data = helpers.getLanguageData()
    
    if logged_user:
        knowed_words = json.loads(get_knowed_words(logged_user))
        # Consulta segura con parámetros de consulta
        query = "SELECT * FROM texts WHERE author_id = %s"
        params = (logged_user['id'],)
        results = helpers.requestDB(query, params)

        readable_results = []
        for result in results:
            readable_results.append({
                'id': result[0],
                'title': result[1],
                'img_src': result[2],
                'stats': json.loads(result[3].decode('utf-8')),
                'text': nagisa.tagging(result[4]).words,
                'author_id': result[5],
                'is_public': result[6]
            })

        return json.dumps({ 'data': { 'texts': readable_results, 'knowed_words': knowed_words } })
    else:
        return json.dumps({ 'error': data['language_data']['text_data']['messages']['error'] })
    
@text_bp.route('/texts/<int:text_id>')
def get_text(text_id):
    logged_user = helpers.getLoggedUser()
    if logged_user:
        # Get language data
        data = helpers.getLanguageData()
        # Put logged user info
        data['logged_user'] = logged_user
        return render_template('text.html', data = data)
    else:
        return redirect(url_for('auth.login'))

@text_bp.route('/texts/getTextAndWords', methods=['POST'])
def get_text_and_words():
    # Get language data
    data = helpers.getLanguageData()

    logged_user = helpers.getLoggedUser()
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
    data = helpers.getLanguageData()

    query = "SELECT * FROM texts WHERE id = %s AND author_id = %s"
    params = (text_id, logged_user['id'])
    results = helpers.requestDB(query, params)

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
    # Consulta segura con parámetros de consulta
    query = "SELECT * FROM words WHERE user_id = %s"
    params = (logged_user['id'],)
    results = helpers.requestDB(query, params)
    
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
    data = helpers.getLanguageData()

    word = request.get_json()['word']
    stats = request.get_json()['stats']
    text_id = request.get_json()['textId']

    logged_user = helpers.getLoggedUser()
    if logged_user:
        query = "SELECT * FROM words WHERE user_id = %s AND word = %s"
        params = (logged_user['id'], word['word'])
        results = helpers.requestDB(query, params)

        # Si ya hay un resultado solo actualizar el dato
        if len(results) > 0:
            # Si es a unknown, eliminar el registro, sino, actualizarlo
            if word['status'] == 'unknown':
                query = "DELETE FROM words WHERE id = %s"
                params = (results[0][0], )
                helpers.requestDB(query, params)
            else:
                query = "UPDATE words SET status = %s WHERE id = %s"
                params = (word['status'], results[0][0])
                helpers.requestDB(query, params)
        else:
            # Si no hay resultados, crear el registro
            query = "INSERT INTO words (user_id, word, status) VALUES (%s, %s, %s)"
            params = (logged_user['id'], word['word'], word['status'])
            helpers.requestDB(query, params)

        # Actualizar los stats del texto
        query = "UPDATE texts SET stats = %s WHERE id = %s"
        params = (stats, text_id)
        helpers.requestDB(query, params)

        return json.dumps({ 'success': data['language_data']['text_data']['messages']['success'] })
    else:
        return json.dumps({ 'error': data['language_data']['text_data']['messages']['error'] })

@text_bp.route('/texts/add')
def add_text():
    logged_user = helpers.getLoggedUser()
    if logged_user:
        # Get language data
        data = helpers.getLanguageData()
        # Put logged user info
        data['logged_user'] = logged_user
        return render_template('add.html', data = data)
    else:
        return redirect(url_for('auth.login'))

@text_bp.route('/texts/addTextBackend', methods=['POST'])
def add_text_backend():
    data = helpers.getLanguageData()

    title = request.get_json()['title']
    img_src = request.get_json()['img_src']
    stats = request.get_json()['stats']
    text = request.get_json()['text']
    author_id = request.get_json()['author_id']
    is_public = request.get_json()['is_public']
    
    # Registro
    query = "INSERT INTO texts (title, img_src, stats, text, author_id, is_public) VALUES (%s, %s, %s, %s, %s, %s);"
    params = (title, img_src, stats, text, author_id, is_public)
    result = helpers.requestDB(query, params)

    if type(result) == int:
        # El registro fue exitoso
        return json.dumps({ 'success': data['language_data']['text_data']['messages']['success'] })
    else:
        # El registro falló
        return json.dumps({ 'error': data['language_data']['text_data']['messages']['error'] })