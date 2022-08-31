import yaml

def __read_config():
    with open('options.yml','r') as file:
        return yaml.load(file.read(), yaml.BaseLoader)

OPTIONS = __read_config()