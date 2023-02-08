import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
from app import app_flask, views
from asgiref.wsgi import WsgiToAsgi
from loguru import logger
logger.add('errors.log', format='{time:DD-MM HH:mm} {message}', level='ERROR',)


asgi_app = WsgiToAsgi(app_flask)

if __name__ == '__main__':
        app_flask.run()
