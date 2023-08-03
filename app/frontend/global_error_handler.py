from loguru import logger
from app.core.data_transfer_objects.answer import RequestResponse


async def global_error(error, rec_request=None, resp_json=RequestResponse(data={}, error={}, meta={})):
    # Глобальный обработчик ошибок для всех непредвиденных ситуаций
    if not rec_request:
        logger.critical(f'GLOBAL_ERROR_500! {error=}, {resp_json=}')
    else:
        logger.critical(f'GLOBAL_ERROR_500! {error=}, rec_request={rec_request.dict(exclude={"token"})}, {resp_json=}')
    resp_json.meta.code = 500
    resp_json.error.error_description = 'Internal Server Error'
    resp_json.error.error_message = str(error)
    return resp_json
