from reuploader import create_app
from reuploader.db import init_db
from sqlite3 import OperationalError

app = create_app()

try:
    with app.app_context():
        init_db()
except OperationalError:
    pass
