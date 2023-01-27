from datetime import datetime, timedelta
from statistics import median
import logging
logging.basicConfig(filename='logs.log', level=logging.ERROR)


def owner_name(owner, name):
    # Однократно передаем владельца и имя репозитория, используется для логирования
    global repo_owner
    global repo_name
    repo_owner = owner
    repo_name = name


def to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')


def parsing_version(data):
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
            logging.error(f'Проверено 100 записей и не найдено версии! Owner: {repo_owner}, name: {repo_name}')
    if not major_v:
        major_v = published_date
    if not minor_v:
        minor_v = published_date
    if not patch_v:
        patch_v = published_date
    major_v = datetime.now() - to_date(major_v)
    minor_v = datetime.now() - to_date(minor_v)
    patch_v = datetime.now() - to_date(patch_v)
    return [major_v.days, minor_v.days, patch_v.days]


def pull_request_analytics(data):
    """
    Анализ 100 последних Pull Request.
    Анализируем только закрытые PR с момента закрытия которых прошло не более 2х месяцев.
    :param data: данные о 100 последних PR (json/GitHub)
    :return:
    count_closed_pr: количество закрытых PR за последние 2 месяца (из 100 последних)
    median_closed_pr: медиана обработки PR в днях, от публикации до согласования (вещественное число)
    """
    duration_pullrequest = []
    count_closed_pr = 0
    for pullrequest in data:
        if pullrequest['closed'] and bool(pullrequest['closedAt']):
            if to_date(pullrequest['closedAt']) + timedelta(60) > datetime.now():
                duration_pullrequest.append(to_date(pullrequest['closedAt']) - to_date(pullrequest['publishedAt']))
                count_closed_pr += 1
    # Медиана времени закрытия PR за последние 2 месяца, умножаем timedelta на 24, вытягиваем дни(фактически это часы)
    # и опять делим на 24 для получения дней с точностью до часа (вещественное число)
    median_closed_pr = median(duration_pullrequest) * 24
    median_closed_pr = median_closed_pr.days / 24
    return [count_closed_pr, median_closed_pr]
