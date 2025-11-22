import tomllib

_config = None

def get_config():
    global _config
    if _config is None:
        try:
            with open("config.toml", "rb") as config_file:
                _config = tomllib.load(config_file)
        except FileNotFoundError:
            print("Config file not found. Please create a config.toml file. Check the README for more information.")
            exit(1)
    return _config