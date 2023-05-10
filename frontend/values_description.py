# Описание значений resp_json
values_description = {
    'data': {
        'owner': 'Имя владельца репозитория (str)',
        'name': 'Имя репозитория (str)',
        'description': 'Описание (str)',
        'stars': 'Количество звезд (int)',
        'createdAt': 'Дата создания (str iso)',
        'existenceTime': 'Как давно существует (int дней)',
        'updatedAt': 'Время с последнего обновления НЕ КОДА (int дней)',
        'pushedAt': 'Время с последнего обновления КОДА, любая ветка (int дней)',
        'version': 'Текущая версия проекта (str)',
        'updMajorVer': 'Время с обновления Мажорной версии (int дней)',
        'updMinorVer': 'Время с обновления Минорной версии (int дней)',
        'updPatchVer': 'Время с обновления Патч версии (int дней)',
        'prClosedCount2m': 'Количество PR закрытых за последние 2 месяца (int)',
        'prClosedDuration': 'Среднее время закрытия PR (float дней)',
        'archived': 'Репозиторий находится в архиве (bool)',
        'locked': 'Репозиторий закрыт (bool)',
        'watchersCount': 'Количество наблюдателей (int)',
        'forkCount': 'Количество форков (int)',
        'issuesCount': 'Общее количество вопросов (int)',
        'bugIssuesCount': 'Общее количество вопросов в которых присутствуют bug метками (int)',
        'bugIssuesClosedCount': 'Количество закрытых bug-вопросов (int)',
        'bugIssuesOpenCount': 'Количество открытых bug-вопросов (int)',
        'bugIssuesNoComment': 'Какой процент bug-вопросов не имеет комментариев (float % max 100.00)',
        'bugIssuesClosed2m': 'Процент bug-вопросов решенных быстрее 2х месяцев, '
                             'от общего числа решенных bug-вопросов (float % max 100.00)',
        'closedBug95perc': 'Медианное значение времени закрытия 95 % bug-вопросов, '
                           'среди всех закрытых bug-вопросов (int дней)',
        'closedBug50perc': 'Медианное значение времени закрытия bug-вопросов, '
                           'среди всех закрытых bug-вопросов (int дней)',
    },
    'error': {
        'errorDescription': 'Описание ошибки (str)',
        'errorMessage': 'Текст ошибки (str)',
    },
    'meta': {
        'code': 'Код ответа (int)',
        'information': 'Информация о запросе (str)',
        'cost': 'Стоимость запроса (int)',
        'remains': 'Остаток кредитов для запросов (int 5000/час)',
        'resetAt': 'Время обнуления кредитов (str iso)',
        'estimatedTime': 'Предполагаемое время запроса (float секунд)',
        'time': 'Фактическое время запроса (float секунд)',
        'requestDowntime': 'Время простоя, ожидание ответа GitHub (float секунд)',
    },
}
