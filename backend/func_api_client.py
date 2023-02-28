from datetime import datetime, timedelta
from statistics import median
from loguru import logger


async def to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')


async def parsing_version(resp_json, data):
    """
    Распарсиваем, дополняем до 3х версий, присваиваем значения по умолчанию и смотрим изменения в цикле.
    Если в считанных записях не находится изменений версии, присваивается самая ранняя считанная дата.
    При наличии 1 версии проекта, все счетчики считаются от нее.
    :param data: даты и версии проекта, 100 последних изменений (json/GitHub)
    :return: количество полных дней с обновления мажорной, минорной и патч версий
    """
    major_v = minor_v = patch_v = None
    version = data[0]['node']['tag']['name'].split('.')
    published_date = data[0]['node']['publishedAt']
    for _ in range(len(version), 3):
        version.append('0')
    old_mj = version[0]
    old_mi = version[1]
    old_pt = version[2]
    for release in data[1:]:
        if major_v and minor_v and patch_v:
            break
        version = (release['node']['tag']['name']).split('.')
        for _ in range(len(version), 3):
            version.append('0')
        if not major_v:
            new_mj = version[0]
            if new_mj != old_mj:
                major_v = published_date
        if not minor_v:
            new_mi = version[1]
            if new_mi != old_mi:
                minor_v = published_date
        if not patch_v:
            new_pt = version[2]
            if new_pt != old_pt:
                patch_v = published_date
        published_date = release['node']['publishedAt']
    else:
        if len(data) == 100:
            logger.error(f'ERROR! Не найдено версии (100 записей), '
                         f'"{resp_json.data.owner}/{resp_json.data.name}".')
    if not major_v: major_v = published_date
    if not minor_v: minor_v = published_date
    if not patch_v: patch_v = published_date
    resp_json.analytic.upd_major_ver = (datetime.utcnow() - await to_date(major_v)).days
    resp_json.analytic.upd_minor_ver = (datetime.utcnow() - await to_date(minor_v)).days
    resp_json.analytic.upd_patch_ver = (datetime.utcnow() - await to_date(patch_v)).days
    return resp_json


async def pull_request_analytics(resp_json, data):
    """
    Анализ 100 последних Pull Request.
    Анализируем только закрытые PR с момента закрытия которых прошло не более 2х месяцев.
    :param data: данные о 100 последних PR (json/GitHub)
    :return: количество PR закрытых за последние 2 месяца, медиану времени закрытия
    """
    duration_pullrequest = []
    count_closed_pr = 0
    for pullrequest in data:
        if pullrequest['closed'] and bool(pullrequest['closedAt']):
            if await to_date(pullrequest['closedAt']) + timedelta(60) > datetime.utcnow():
                duration_pullrequest.append(await to_date(pullrequest['closedAt']) - await to_date(pullrequest['publishedAt']))
                count_closed_pr += 1
    # Медиана времени закрытия PR за последние 2 месяца, умножаем timedelta на 24, вытягиваем дни(фактически это часы)
    # и опять делим на 24 для получения дней с точностью до часа (вещественное число)
    median_closed_pr = median(duration_pullrequest) * 24
    resp_json.analytic.pr_closed_duration = round(median_closed_pr.days / 24, 3)
    resp_json.analytic.pr_closed_count = count_closed_pr
    return resp_json


async def path_error_400(resp_json, repository_path, e):
    logger.error(f'E400! Не распознан repository_path="{repository_path}", e="{e}".')
    resp_json.meta.code = 400
    resp_json.meta.error_desc = 'Bad repository adress'
    resp_json.meta.error_message = "Bad repository adress, enter the address in the format 'https://github.com/Vi-812/git_check_alive' or 'vi-812/git_check_alive'."
    return resp_json


async def json_error_401(resp_json, repository_owner, repository_name, e_data):
    logger.error(f'E401! Ошибка токена, обращались к "{repository_owner}/{repository_name}", e_data="{e_data}".')
    resp_json.meta.code = 401
    resp_json.meta.error_desc = 'Token error, invalid token'
    resp_json.meta.error_message = str(e_data)
    return resp_json


async def json_error_404(resp_json, repository_owner, repository_name, error):
    logger.error(f'E404! Не найден репозиторий "{repository_owner}/{repository_name}".')
    resp_json.meta.code = 404
    resp_json.meta.error_desc = 'Repository not found'
    resp_json.meta.error_message = str(error)
    resp_json.meta.cost = 1
    return resp_json
