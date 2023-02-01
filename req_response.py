from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RepositoryInfo(BaseModel):
    owner: Optional[str]
    name: Optional[str]
    description: Optional[str]
    stars: Optional[int]
    version: Optional[str]
    created_at: Optional[datetime]
    duration: Optional[int]
    updated_at: Optional[int]
    pushed_at: Optional[int]
    archived: Optional[bool]
    locked: Optional[bool]
    issues_count: Optional[int]
    bug_issues_count: Optional[int]
    bug_issues_closed_count: Optional[int]
    bug_issues_open_count: Optional[int]
    watchers_count: Optional[int]
    fork_count: Optional[int]


class Analytic(BaseModel):
    bugs_closed_time_95percent: Optional[int]
    bugs_closed_time_50percent: Optional[int]
    major_days_passed: Optional[int]
    minor_days_passed: Optional[int]
    patch_days_passed: Optional[int]
    percent_issues_no_comment: Optional[float]
    percent_issues_closed_2months: Optional[float]
    pull_request_closed_2months: Optional[int]
    median_duration_pull_request: Optional[float]


class QueryInfo(BaseModel):
    code: Optional[int] = 0
    error_desc: Optional[str]
    error_message: Optional[str]
    cost: Optional[int] = 0
    time: Optional[float]
    remains: Optional[int]
    reset_at: Optional[str]
    database: Optional[str]
    rt: Optional[str]


class RequestResponse(BaseModel):
    repository_info: RepositoryInfo
    analytic: Analytic
    query_info: QueryInfo


resp_json = RequestResponse(repository_info={}, analytic={}, query_info={})
