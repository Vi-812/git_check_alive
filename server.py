import os
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
from frontend import app_sanic, views, models
from loguru import logger
logger.add('errors.log', format='{time:DD-MM HH:mm} {message}', level='ERROR',)
logger.add('info.log', format='{time:DD-MM HH:mm} {message}', level='INFO',)

if __name__ == '__main__':
    app_sanic.run()
    models.RepositoryInfo.create_database_table()
    models.QueryStatistics.create_database_table()
    models.RepositoryCollection.create_database_table()
