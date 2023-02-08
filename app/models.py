from app import db
from sqlalchemy import Column, DateTime, func


class RepositoryInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upd_date = db.Column(db.DateTime, onupdate=func.now(), default=func.now(), nullable=False)
    repo_path = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=True)
    stars = db.Column(db.Integer, nullable=False)
    version = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.Integer, nullable=False)
    pushed_at = db.Column(db.Integer, nullable=False)
    archived = db.Column(db.Boolean, nullable=False)
    locked = db.Column(db.Boolean, nullable=False)
    issues_count = db.Column(db.Integer, nullable=False)
    bug_issues_count = db.Column(db.Integer, nullable=False)
    bug_issues_closed_count = db.Column(db.Integer, nullable=False)
    bug_issues_open_count = db.Column(db.Integer, nullable=False)
    watchers_count = db.Column(db.Integer, nullable=False)
    fork_count = db.Column(db.Integer, nullable=False)
    closed_bug_95perc = db.Column(db.Integer, nullable=True)
    closed_bug_50perc = db.Column(db.Integer, nullable=True)
    upd_major_ver = db.Column(db.Integer, nullable=True)
    upd_minor_ver = db.Column(db.Integer, nullable=True)
    upd_patch_ver = db.Column(db.Integer, nullable=True)
    bug_issues_no_comment = db.Column(db.Float, nullable=True)
    bug_issues_closed_2months = db.Column(db.Float, nullable=True)
    pr_closed_count = db.Column(db.Integer, nullable=True)
    pr_closed_duration = db.Column(db.Float, nullable=True)
    time = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<{self.repo_path}>'


class QueryStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crt_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    repo_path = db.Column(db.String, nullable=False)
    issues_count = db.Column(db.Integer, nullable=False)
    bug_issues_count = db.Column(db.Integer, nullable=False)
    time = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    request_kf = db.Column(db.Float, nullable=False)
    query_limit = db.Column(db.Integer, nullable=True)
    rt = db.Column(db.String, nullable=True)


class RepositoryCollection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crt_date = db.Column(db.DateTime, default=func.now(), nullable=False)
    repo_path = db.Column(db.String, unique=True, nullable=False)
    token_hash = db.Column(db.String, nullable=False)
    saved = db.Column(db.Boolean, default=False, nullable=False)
