from os import environ
from dotenv import find_dotenv, load_dotenv
import json

dotenv_file = find_dotenv()
if not dotenv_file:
    f = open('.env', 'x')
    f.close()
    dotenv_file = find_dotenv()
load_dotenv(dotenv_file)  # load secret keys

GOOGLE_CLIENT_SECRET = environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_CLIENT_ID = environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_DISCOVERY_URL = environ.get("GOOGLE_DISCOVERY_URL", None)
YANDEX_CLIENT_ID = environ.get("YANDEX_CLIENT_ID", None)
YANDEX_CLIENT_SECRET = environ.get("YANDEX_CLIENT_SECRET", None)
YANDEX_DISCOVERY_URL = environ.get("YANDEX_DISCOVERY_URL", None)
YANDEX_REDIRECT_URI = environ.get("YANDEX_REDIRECT_URI", None)

APPROVED_EMAILS = json.loads(environ.get("APPROVED_EMAILS", '[]'))

