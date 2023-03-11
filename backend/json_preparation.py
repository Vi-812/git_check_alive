from datetime import datetime
from loguru import logger
import redis
redis = redis.Redis(host='51.68.189.155')


async def final_json_preparation(rec_request, resp_json):
    code = resp_json.meta.code
    if code == 200:
        resp_json.__delattr__('error')
        if not resp_json.meta.information:
            time = datetime.utcnow().isoformat()
            resp_json.meta.information = f'Relevant  information at {time} UTC'
        if rec_request.response_type == 'repo':
            resp_json.data.__delattr__('bug_issues_count')
            resp_json.data.__delattr__('bug_issues_closed_count')
            resp_json.data.__delattr__('bug_issues_open_count')
            resp_json.data.__delattr__('bug_issues_no_comment')
            resp_json.data.__delattr__('bug_issues_closed2m')
            resp_json.data.__delattr__('closed_bug_95perc')
            resp_json.data.__delattr__('closed_bug_50perc')
        else:
            # Если у нас полный запрос подвешиваем json в Redis
            await redis_set(resp_json=resp_json)
        if rec_request.response_type == 'issues':
            resp_json.data.__delattr__('description')
            resp_json.data.__delattr__('stars')
            resp_json.data.__delattr__('created_at')
            resp_json.data.__delattr__('duration')
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
        resp_json.__delattr__('data')
    return resp_json.json(by_alias=True), code


async def redis_set(resp_json):
    try:
        redis.set(
            resp_json.data.owner + '/' + resp_json.data.name,
            resp_json.json(by_alias=True)
        )
    except ConnectionError as e:
        logger.error(f'ConnectionError! {e=}')
    except Exception as e:
        logger.error(f'Exception/ConnectionError! {e=}')
