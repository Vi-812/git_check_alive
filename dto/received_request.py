from pydantic import BaseModel
from typing import Optional


class ReceivedRequest(BaseModel):
    url: str
    repo_path: Optional[str]
    token: str
    force: Optional[bool] = False
    response_type: Optional[str] = 'full'
    repo_owner: Optional[str]
    repo_name: Optional[str]
