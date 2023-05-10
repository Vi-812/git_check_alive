import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
from frontend import app, views
from loguru import logger
import uvicorn

logger.add('log_err.log', format='{time} {level} {message}', level='ERROR')
logger.add('log_warn.log', format='{time} {level} {message}', level='WARNING')
logger.add('log_info.log', format='{time:DD-MM HH:mm} {message}', level='INFO')

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
