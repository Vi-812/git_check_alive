from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta


class Data(BaseModel):
    owner: Optional[str]
    name: Optional[str]
    description: Optional[str]
    stars: Optional[int]
    version: Optional[str]
    created_at: Optional[datetime] = Field(alias='createdAt')
    duration: Optional[int]
    updated_at: Optional[int] = Field(alias='updatedAt')
    pushed_at: Optional[int] = Field(alias='pushedAt')
    archived: Optional[bool]
    locked: Optional[bool]
    issues_count: Optional[int] = Field(alias='issuesCount')
    bug_issues_count: Optional[int] = Field(alias='bugIssuesCount')
    bug_issues_closed_count: Optional[int] = Field(alias='bugIssuesClosedCount')
    bug_issues_open_count: Optional[int] = Field(alias='bugIssuesOpenCount')
    watchers_count: Optional[int] = Field(alias='watchersCount')
    fork_count: Optional[int] = Field(alias='forkCount')


class Analytic(BaseModel):
    closed_bug_95perc: Optional[int] = Field(alias='closedBug95perc')
    closed_bug_50perc: Optional[int] = Field(alias='closedBug50perc')
    upd_major_ver: Optional[int] = Field(alias='updMajorVer')
    upd_minor_ver: Optional[int] = Field(alias='updMinorVer')
    upd_patch_ver: Optional[int] = Field(alias='updPatchVer')
    bug_issues_no_comment: Optional[float] = Field(alias='bugIssuesNoComment')
    bug_issues_closed_2months: Optional[float] = Field(alias='bugIssuesClosed2months')
    pr_closed_count: Optional[int] = Field(alias='prClosedCount')
    pr_closed_duration: Optional[float] = Field(alias='prClosedDuration')


class Meta(BaseModel):
    code: Optional[int] = 0
    error_desc: Optional[str] = Field(alias='errorDesc')
    error_message: Optional[str] = Field(alias='errorMessage')
    cost: Optional[int] = 0
    time: Optional[float]
    remains: Optional[int]
    reset_at: Optional[str] = Field(alias='resetAt')
    database: Optional[str]
    rt: Optional[str]
    ght: Optional[datetime] = timedelta(seconds=0)


class RequestResponse(BaseModel):
    data: Data
    analytic: Analytic
    meta: Meta
