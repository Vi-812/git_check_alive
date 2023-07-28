from pydantic import BaseModel
from typing import Optional


# DTO с данными по запросу
class ReceivedRequest(BaseModel):
    url: str  # URL на который пришел запрос
    repo_path: Optional[str]  # Переданный адрес репозитория
    token: str  # Токен для доступа
    skip_cache: Optional[bool] = False  # skip_cache = True, минует загрузку из БД, принудительно обновляем
    response_type: Optional[str] = 'full'  # Тип запроса repo/issues/full
    repo_owner: Optional[str]  # Владелец репозитория (распознано из repo_path)
    repo_name: Optional[str]  # Имя репозитория (распознано из repo_path)
