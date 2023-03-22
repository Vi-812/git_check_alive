from loguru import logger


async def path_error_400(rec_request, resp_json, repository_path, e=None):
    # Обработка ошибки при неверной передаче repository_path
    logger.warning(f'E_400! Не распознан {repository_path=}, {e=}, rec_request={rec_request.dict(exclude={"token"})}')
    resp_json.meta.code = 400
    resp_json.error.error_description = 'Bad repository address'
    resp_json.error.error_message = "Bad repository address, enter the address in the format " \
                              "'https://github.com/Vi-812/git_check_alive' or 'vi-812/git_check_alive'."
    return resp_json


async def json_error_401(rec_request, resp_json, e_data):
    # Обработка ошибки при неверном token
    logger.warning(f'E_401! Ошибка токена! {e_data=}, rec_request={rec_request.dict(exclude={"token"})}')
    resp_json.meta.code = 401
    resp_json.error.error_description = 'Token error, invalid token'
    resp_json.error.error_message = str(e_data)
    return resp_json


async def json_error_404(rec_request, resp_json, error, e):
    # Обработка ошибки если репозиторий не найден на GitHub
    logger.warning(f'E_404! Не найден репозиторий! rec_request={rec_request.dict(exclude={"token"})}, {error=}, {e=}')
    resp_json.meta.code = 404
    resp_json.error.error_description = 'Repository not found'
    resp_json.error.error_message = str(error)
    resp_json.meta.cost = 1
    return resp_json


async def connection_error_500(rec_request, resp_json, error):
    # Обработка ошибки соединения с GitHub
    logger.error(f'E_500! Ошибка соединения с сервером, {error=}, rec_request={rec_request.dict(exclude={"token"})}')
    resp_json.meta.code = 500
    resp_json.error.error_description = 'Server Connection Error'
    resp_json.error.error_message = str(error)
    return resp_json


async def internal_error_500(rec_request, resp_json, e_data, error=None):
    # Обработка ошибки при некорректном ответе data от GitHub
    logger.error(f'GET_DATA_ERROR_500! Ошибка в полученной data! '
                   f'rec_request={rec_request.dict(exclude={"token"})}, {e_data=}, {error=}')
    resp_json.meta.code = 500
    resp_json.error.error_description = 'Internal Server Error'
    resp_json.error.error_message = str(error)
    resp_json.meta.cost = 1
    return resp_json
