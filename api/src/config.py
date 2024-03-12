from dotenv import find_dotenv, load_dotenv
def startup_callback(env_file: str | None = None):
    if env_file:
        load_dotenv(find_dotenv(filename=env_file))
    else:
        load_dotenv(find_dotenv())
    return