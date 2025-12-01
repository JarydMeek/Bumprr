import tomllib

_config = None

def get_config():
    global _config
    if _config is None:
        try:
            with open("config/config.toml", "rb") as config_file:
                _config = tomllib.load(config_file)
        except FileNotFoundError:
            print("Config file not found. Creating a default config/config.toml... Please edit it and restart the application according to the README instructions.")
            with open("config-example.toml", "rb") as example_file:
                example_content = example_file.read()
            with open("config/config.toml", "wb") as config_file:
                config_file.write(example_content)
            exit(1)
    return _config

def add_to_config(section, key, value):
    config = get_config()
    if section not in config:
        config[section] = {}
    config[section][key] = value