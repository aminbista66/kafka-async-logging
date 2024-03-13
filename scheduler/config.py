from dotenv import find_dotenv, load_dotenv

def load_env_callback(env_file: str | None = None):
    if env_file:
        load_dotenv(find_dotenv(filename=env_file))
    else:
        load_dotenv(find_dotenv())
    return