from configparser import ConfigParser
from flask import session
import json, mysql.connector, helpers

def readConfig(category, attribute, is_int = False):
    config = ConfigParser()
    config.read('config.ini')
    if is_int:
        return config.getint(category, attribute)
    else:
        return config[category][attribute]

def getLanguageData():
    config = readConfig('APP', 'LANGUAGE')
    with open('language_texts.json') as json_file:
        data = json.load(json_file)
        local_language_data = list(filter(lambda language: language['language'] == config, data['languages']))
        return local_language_data[0] or {}
    
def getLoggedUser():
    return session.get('logged_user')

def requestDB(query, params):
    cn = mysql.connector.connect(
        host = helpers.readConfig('DATABASE', 'HOST'),
        port = helpers.readConfig('DATABASE', 'PORT', True),
        user = helpers.readConfig('DATABASE', 'USER'),
        password = helpers.readConfig('DATABASE', 'PASSWORD'),
        database = helpers.readConfig('DATABASE', 'DATABASE')
    )
    cursor = cn.cursor()
    
    results = []
    cursor.execute(query, params)

    if query.startswith("SELECT"):
        results = cursor.fetchall()
    else:
        cn.commit()
        results = cursor.rowcount

    cursor.close()
    cn.close()
    return results