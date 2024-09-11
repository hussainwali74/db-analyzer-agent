import json

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)
        
def get_openai_model():
    config = load_config()
    return config.get('openai_model', 'gpt-4o-mini')

