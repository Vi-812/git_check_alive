import logging
from datetime import datetime

logging.basicConfig(filename='logs.log', level=logging.INFO)


def to_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')


def parsing_version(data):
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
            logging.error('Проверено 100 записей, не найдено версии!', published_date)
    major_v = datetime.now() - to_date(major_v)
    minor_v = datetime.now() - to_date(minor_v)
    patch_v = datetime.now() - to_date(patch_v)
    return [major_v.days, minor_v.days, patch_v.days]
