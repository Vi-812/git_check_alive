from pydantic import BaseModel
from typing import Dict, Union


class QueryInfo(BaseModel):
    code: int
    time: float
    cost: int
    remains: int
    resetAt: str
    database: str
    rt: str


class Answer(BaseModel):
    query_info: QueryInfo


