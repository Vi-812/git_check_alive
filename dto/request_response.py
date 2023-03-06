from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Data(BaseModel):
    owner: Optional[str]
    name: Optional[str]
    description: Optional[str]
    stars: Optional[int]
    created_at: Optional[datetime] = Field(alias='createdAt')
    duration: Optional[int]
    updated_at: Optional[int] = Field(alias='updatedAt')
    pushed_at: Optional[int] = Field(alias='pushedAt')
    version: Optional[str]
    upd_major_ver: Optional[int] = Field(alias='updMajorVer')
    upd_minor_ver: Optional[int] = Field(alias='updMinorVer')
    upd_patch_ver: Optional[int] = Field(alias='updPatchVer')
    pr_closed_count2m: Optional[int] = Field(alias='prClosedCount2m')
    pr_closed_duration: Optional[float] = Field(alias='prClosedDuration')
    archived: Optional[bool]
    locked: Optional[bool]
    watchers_count: Optional[int] = Field(alias='watchersCount')
    fork_count: Optional[int] = Field(alias='forkCount')
    issues_count: Optional[int] = Field(alias='issuesCount')
    bug_issues_count: Optional[int] = Field(alias='bugIssuesCount')
    bug_issues_closed_count: Optional[int] = Field(alias='bugIssuesClosedCount')
    bug_issues_open_count: Optional[int] = Field(alias='bugIssuesOpenCount')
    bug_issues_no_comment: Optional[float] = Field(alias='bugIssuesNoComment')
    bug_issues_closed2m: Optional[float] = Field(alias='bugIssuesClosed2m')
    closed_bug_95perc: Optional[int] = Field(alias='closedBug95perc')
    closed_bug_50perc: Optional[int] = Field(alias='closedBug50perc')


class Error(BaseModel):
    description: Optional[str]
    message: Optional[str]


class Meta(BaseModel):
    code: Optional[int] = 0
    information: Optional[str]
    cost: Optional[int] = 0
    remains: Optional[int]
    reset_at: Optional[str] = Field(alias='resetAt')
    estimated_time: Optional[float] = Field(alias='estimatedTime')
    time: Optional[float]
    request_downtime: Optional[datetime] = Field(alias='requestDowntime')


class RequestResponse(BaseModel):
    data: Data
    error: Error
    meta: Meta
