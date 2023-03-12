from datetime import datetime, timedelta
from statistics import median
from loguru import logger


async def to_date(date_str: str) -> datetime:  # Преобразуем из БД в DateTime
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')


async def parsing_version(resp_json, data: list):
    """
    Парсим, дополняем до 3-х версий, присваиваем значения по умолчанию и смотрим изменения в цикле.
    Если в считанных записях не находится изменений версии, присваивается самая ранняя считанная дата.
    При наличии 1 версии проекта, все счетчики считаются от нее.
    :param resp_json: RequestResponse (DTO), для ответа
    :param data: даты и версии проекта, 100 последних изменений (json/GitHub)
    :return: количество полных дней с обновления мажорной, минорной и патч версий
    """
    major_v = minor_v = patch_v = None  # Присваиваем начальные значения
    version = data[0]['node']['tag']['name'].split('.')
    published_date = data[0]['node']['publishedAt']
    for _ in range(len(version), 3):
        version.append('0')
    old_mj = version[0]
    old_mi = version[1]
    old_pt = version[2]  # Присваиваем начальные значения

    for release in data[1:]:  # Перебираем полученные версии
        if major_v and minor_v and patch_v:  # Если все три версии найдены break
            break
        version = (release['node']['tag']['name']).split('.')  # Разбиваем версию на части
        for _ in range(len(version), 3):  # Дополняем части до трех штук
            version.append('0')
        if not major_v:  # Если дата изменения версии еще не найдена
            new_mj = version[0]  # Достаем новую версию
            if new_mj != old_mj:  # Смотрим, изменилась ли версия
                major_v = published_date  # Если изменилась - то фиксируем дату
        if not minor_v:
            new_mi = version[1]
            if new_mi != old_mi:
                minor_v = published_date
        if not patch_v:
            new_pt = version[2]
            if new_pt != old_pt:
                patch_v = published_date
        published_date = release['node']['publishedAt']  # Обновляем дату
    else:
        if len(data) == 100:  # Если проверено 100 записей и не найдена какая-то из версий, записываем warning
            logger.warning(f'Не найдено версии (100 записей)!, {resp_json=}')
    if not major_v: major_v = published_date  # Присваиваем последнюю дату если не найдено изменения версии
    if not minor_v: minor_v = published_date
    if not patch_v: patch_v = published_date
    resp_json.data.upd_major_ver = (datetime.utcnow() - await to_date(major_v)).days  # Высчитываем количество
    resp_json.data.upd_minor_ver = (datetime.utcnow() - await to_date(minor_v)).days  # прошедших дней с последнего
    resp_json.data.upd_patch_ver = (datetime.utcnow() - await to_date(patch_v)).days  # обновления
    return resp_json


async def pull_request_analytics(resp_json, data):
    """
    Анализ 100 последних Pull Request.
    Анализируем только закрытые PR с момента закрытия которых прошло не более 2х месяцев.
    :param resp_json: RequestResponse (DTO), для ответа
    :param data: данные о 100 последних PR (json/GitHub)
    :return: количество PR закрытых за последние 2 месяца, медиану времени закрытия
    """
    duration_pullrequest = []
    count_closed_pr = 0
    for pullrequest in data:  # Перебираем полученные PR
        if pullrequest['closed'] and bool(pullrequest['closedAt']):  # Если PR закрыт
            if await to_date(pullrequest['closedAt']) + timedelta(days=60) > datetime.utcnow():  # За последние 60 дней
                duration_pullrequest.append(  # Добавляем в список продолжительность PR
                    await to_date(pullrequest['closedAt']) - await to_date(pullrequest['publishedAt'])
                )
                count_closed_pr += 1  # Считаем количество закрытых PR

    # Медиана времени закрытия PR за последние 2 месяца, умножаем timedelta на 24, вытягиваем дни(фактически это часы)
    # и опять делим на 24 для получения дней с точностью до часа (вещественное число)
    if duration_pullrequest:
        median_closed_pr = median(duration_pullrequest) * 24
        resp_json.data.pr_closed_duration = round(median_closed_pr.days / 24, 3)
    else:
        resp_json.data.pr_closed_duration = None
    resp_json.data.pr_closed_count2m = count_closed_pr
    return resp_json


async def path_error_400(rec_request, resp_json, repository_path, e):
    # Обработка ошибки при неверной передаче repository_path
    logger.warning(f'E_400! Не распознан {repository_path=}, {e=}, rec_request={rec_request.dict(exclude={"token"})}')
    resp_json.meta.code = 400
    resp_json.error.description = 'Bad repository address'
    resp_json.error.message = "Bad repository address, enter the address in the format " \
                              "'https://github.com/Vi-812/git_check_alive' or 'vi-812/git_check_alive'."
    return resp_json


async def json_error_401(rec_request, resp_json, e_data):
    # Обработка ошибки при неверном token
    logger.warning(f'E_401! Ошибка токена! {e_data=}, rec_request={rec_request.dict(exclude={"token"})}')
    resp_json.meta.code = 401
    resp_json.error.description = 'Token error, invalid token'
    resp_json.error.message = str(e_data)
    return resp_json


async def json_error_404(rec_request, resp_json, error, e):
    # Обработка ошибки если репозиторий не найден на GitHub
    logger.warning(f'E_404! Не найден репозиторий! rec_request={rec_request.dict(exclude={"token"})}, {error=}, {e=}')
    resp_json.meta.code = 404
    resp_json.error.description = 'Repository not found'
    resp_json.error.message = str(error)
    resp_json.meta.cost = 1
    return resp_json


async def internal_error_500(rec_request, resp_json, e_data, error):
    # Обработка ошибки при некорректном ответе data от GitHub
    logger.warning(f'E_500! Ошибка в полученной data! '
                   f'rec_request={rec_request.dict(exclude={"token"})}, {error=}, {e_data=}')
    resp_json.meta.code = 500
    resp_json.error.description = 'Internal Server Error'
    resp_json.error.message = str(error)
    resp_json.meta.cost = 1
    return resp_json
