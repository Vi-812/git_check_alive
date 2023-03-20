from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Data(BaseModel):
    owner: Optional[str]  # Владелец репозитория
    name: Optional[str]  # Имя репозитория
    description: Optional[str]  # Описание
    stars: Optional[int]  # Количество звезд
    created_at: Optional[datetime] = Field(alias='createdAt')  # Дата создания
    duration: Optional[int]  # Продолжительность, количество полных дней
    updated_at: Optional[int] = Field(alias='updatedAt')  # Количество полных дней с обновления
    pushed_at: Optional[int] = Field(alias='pushedAt')  # Количество полных дней с последнего push'а
    version: Optional[str]  # Версия
    upd_major_ver: Optional[int] = Field(alias='updMajorVer')  # Количество полных дней с обновления мажорной версии
    upd_minor_ver: Optional[int] = Field(alias='updMinorVer')  # Количество полных дней с обновления минорной версии
    upd_patch_ver: Optional[int] = Field(alias='updPatchVer')  # Количество полных дней с обновления патч версии
    pr_closed_count2m: Optional[int] = Field(alias='prClosedCount2m')  # Количество PR закрытых за 2 месяца
    pr_closed_duration: Optional[float] = Field(alias='prClosedDuration')  # Среднее время закрытия PR
    archived: Optional[bool]  # Репозиторий в архиве
    locked: Optional[bool]  # Репозиторий закрыт
    watchers_count: Optional[int] = Field(alias='watchersCount')  # Количество наблюдателей
    fork_count: Optional[int] = Field(alias='forkCount')  # Количество форков
    issues_count: Optional[int] = Field(alias='issuesCount')  # Количество issues
    bug_issues_count: Optional[int] = Field(alias='bugIssuesCount')  # Количество issues с bug меткой
    bug_issues_closed_count: Optional[int] = Field(alias='bugIssuesClosedCount')  # Количество закрытых bug_issues
    bug_issues_open_count: Optional[int] = Field(alias='bugIssuesOpenCount')  # Количество открытых bug_issues
    bug_issues_no_comment: Optional[float] = Field(alias='bugIssuesNoComment')  # Количество bug_issues без комментария
    bug_issues_closed2m: Optional[float] = Field(alias='bugIssuesClosed2m')  # Количество bug_issues закрытых менее
    # чем за 2 месяца (не последние 2 месяца)
    closed_bug_95perc: Optional[int] = Field(alias='closedBug95perc')  # За какое среднее время было закрыто 95
    # процентов bug_issues (в днях)
    closed_bug_50perc: Optional[int] = Field(alias='closedBug50perc')  # За какое среднее время было закрыто 50
    # процентов bug_issues (в днях)


class Error(BaseModel):
    description: Optional[str]  # Описание ошибки
    message: Optional[str]  # Сообщение ошибки


class Meta(BaseModel):
    code: Optional[int] = 0  # Код запроса
    information: Optional[str]  # Информационный блок
    cost: Optional[int] = 0  # Стоимость запроса
    remains: Optional[int]  # Остаток кредитов
    reset_at: Optional[str] = Field(alias='resetAt')  # Время сброса кредитов
    estimated_time: Optional[float] = Field(alias='estimatedTime')  # Предпологаемое время запроса
    time: Optional[float]  # Фактическое время запроса
    request_downtime: Optional[datetime] = Field(alias='requestDowntime')  # Время простоя, ожидание ответа GitHub


class RequestResponse(BaseModel):  # DTO для формирования ответа на запрос
    data: Data  # Запрашиваемые данные
    error: Error  # Ошибка, если есть
    meta: Meta  # Служебная информация
