from configparser import ConfigParser
import json

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