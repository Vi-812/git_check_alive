import os
import redis
from redis.exceptions import AuthenticationError, ConnectionError, TimeoutError
from datetime import datetime
from loguru import logger
from dotenv import load_dotenv
load_dotenv()

redis = redis.Redis(  # Создаем экземпляр Redis
    host='51.68.189.155',
    password=os.getenv('REQUIREPASS'),
)


async def final_json_preparation(rec_request, resp_json):
    code = resp_json.meta.code  # Получаем код resp_json
    if code == 200:
        resp_json.__delattr__('error')  # Если код 200, убираем поле error
        if not resp_json.meta.information:
            time = datetime.utcnow().isoformat()
            resp_json.meta.information = f'Relevant  information at {time} UTC'
        if rec_request.response_type == 'repo':  # Убираем неактуальные поля
            resp_json.data.__delattr__('bug_issues_count')
            resp_json.data.__delattr__('bug_issues_closed_count')
            resp_json.data.__delattr__('bug_issues_open_count')
            resp_json.data.__delattr__('bug_issues_no_comment')
            resp_json.data.__delattr__('bug_issues_closed2m')
            resp_json.data.__delattr__('closed_bug_95perc')
            resp_json.data.__delattr__('closed_bug_50perc')
        else:
            # Если у нас полный запрос подвешиваем в Redis
            await redis_set(resp_json=resp_json)
        if rec_request.response_type == 'issues':  # Убираем неактуальные поля
            resp_json.data.__delattr__('description')
            resp_json.data.__delattr__('stars')
            resp_json.data.__delattr__('created_at')
            resp_json.data.__delattr__('existence_time')
            resp_json.data.__delattr__('updated_at')
            resp_json.data.__delattr__('pushed_at')
            resp_json.data.__delattr__('version')
            resp_json.data.__delattr__('upd_major_ver')
            resp_json.data.__delattr__('upd_minor_ver')
            resp_json.data.__delattr__('upd_patch_ver')
            resp_json.data.__delattr__('pr_closed_count2m')
            resp_json.data.__delattr__('pr_closed_duration')
            resp_json.data.__delattr__('archived')
            resp_json.data.__delattr__('locked')
            resp_json.data.__delattr__('watchers_count')
            resp_json.data.__delattr__('fork_count')
    else:
        resp_json.__delattr__('data')  # Если код ошибки, убираем поле data
    return resp_json.json(by_alias=True), code  # Возвращаем resp_json в формате json (НЕ словарь), код ответа


async def redis_set(resp_json):  # Подвешиваем json в Redis
    try:
        redis.set(
            resp_json.data.owner + '/' + resp_json.data.name,
            resp_json.json(by_alias=True)
        )
    except AuthenticationError as e:
        logger.error(f'AuthenticationError! {e=}')
    except ConnectionError as e:
        logger.error(f'ConnectionError! {e=}')
    except TimeoutError as e:
        logger.error(f'TimeoutError! {e=}')
    except Exception as e:
        logger.error(f'Unknown Redis Exception! {e=}')
