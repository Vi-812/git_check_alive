from datetime import datetime
import logging
logging.basicConfig(filename='logs.log', level=logging.ERROR)



def owner_name(owner, name):
    global repo_owner
    global repo_name
    repo_owner = owner
    repo_name = name

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
            logging.error(f'Проверено 100 записей и не найдено версии! Owner: {repo_owner}, name: {repo_name}, '
                          f'дата: {published_date}')
    # Проверить существование данных
    major_v = datetime.now() - to_date(major_v)
    minor_v = datetime.now() - to_date(minor_v)
    patch_v = datetime.now() - to_date(patch_v)
    return [major_v.days, minor_v.days, patch_v.days]

def pull_request_analytics(data):
    duration_closed_pullrequest = []
    date_closed_pullrequest = []
    for pullrequest in data:
        if pullrequest['closed'] and bool(pullrequest['closedAt']):
            duration_closed_pullrequest.append(to_date(pullrequest['closedAt']) - to_date(pullrequest['publishedAt']))
            date_closed_pullrequest.append(to_date(pullrequest['closedAt']))



    print(duration_closed_pullrequest)
    print(date_closed_pullrequest)
    if len(duration_closed_pullrequest) == len(date_closed_pullrequest):
        print(len(date_closed_pullrequest))
