import os
from sanic import Sanic
from sanic_jinja2 import SanicJinja2
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
token_flask = os.getenv('TOKEN')

app_sanic = Sanic(name='git_check_alive')
jinja = SanicJinja2(app_sanic, pkg_name="main")

APP_DIR = os.path.abspath(os.path.dirname('__init__.py'))
DB_DIR = os.path.join(APP_DIR, 'instance')
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

db = create_engine('sqlite:///' + os.path.join(DB_DIR, 'repositories.db'))
from app import models






# db = create_engine('sqlite:///' + os.path.join(DB_DIR, 'repositories.db'), encoding='utf-8')

    # ('sqlite:///' + os.path.join(PROJECT_DIR, 'database', 'platform.db'))



# import asyncio
# loop = asyncio.get_event_loop()


# app_flask = Flask(__name__)
# app_flask.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


# app_flask.config['SQLALCHEMY_DATABASE_URI']
# app_flask.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(db_dir, 'db_migrate')
# db = SQLAlchemy(app_flask)
# migrate = Migrate(app_flask, db)

# from app import models

# with app_flask.app_context():
#     db.create_all()
