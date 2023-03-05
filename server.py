import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
from frontend import app_sanic, views
from loguru import logger

logger.add('log_err.log', format='{time} {level} {message}', level='ERROR')
logger.add('log_warn.log', format='{time} {level} {message}', level='WARNING')
logger.add('log_info.log', format='{time:DD-MM HH:mm} {message}', level='INFO')

if __name__ == '__main__':
    app_sanic.run()
