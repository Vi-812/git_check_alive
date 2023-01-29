from app import db
from datetime import datetime


class RepositoryInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upd_date = db.Column(db.DateTime, onupdate=datetime.utcnow(), default=datetime.utcnow())
    name = db.Column(db.String, nullable=False)
    owner_login = db.Column(db.String, nullable=False)  # unique=True
    description = db.Column(db.String, nullable=True)
    stars_count = db.Column(db.Integer, nullable=False)
    version = db.Column(db.String, nullable=True)
    created_at = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.Integer, nullable=False)
    pushed_at = db.Column(db.Integer, nullable=False)
    is_archived = db.Column(db.Boolean, nullable=False)
    is_locked = db.Column(db.Boolean, nullable=False)
    issues_count = db.Column(db.Integer, nullable=False)
    bug_issues_count = db.Column(db.Integer, nullable=False)
    bug_issues_closed_count = db.Column(db.Integer, nullable=False)
    bug_issues_open_count = db.Column(db.Integer, nullable=False)
    watchers_count = db.Column(db.Integer, nullable=False)
    fork_count = db.Column(db.Integer, nullable=False)
    closed_bug_95percent = db.Column(db.Integer, nullable=True)
    closed_bug_50percent = db.Column(db.Integer, nullable=True)
    upd_major_ver = db.Column(db.Integer, nullable=True)
    upd_minor_ver = db.Column(db.Integer, nullable=True)
    upd_path_ver = db.Column(db.Integer, nullable=True)
    bug_issues_no_comment = db.Column(db.Float, nullable=True)
    bug_issues_closed_two_months = db.Column(db.Float, nullable=True)
    pr_closed_count = db.Column(db.Integer, nullable=True)
    pr_closed_duration = db.Column(db.Integer, nullable=True)
    request_time = db.Column(db.Float, nullable=False)
    request_cost = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<{self.owner_login}/{self.name}>'


class QueryStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crt_date = db.Column(db.DateTime, default=datetime.utcnow())
    name = db.Column(db.String, nullable=False)
    owner_login = db.Column(db.String, nullable=False)
    issues_count = db.Column(db.Integer, nullable=False)
    bug_issues_count = db.Column(db.Integer, nullable=False)
    request_time = db.Column(db.Float, nullable=False)
    request_cost = db.Column(db.Integer, nullable=False)
    request_kf = db.Column(db.Float, nullable=False)
    rt = db.Column(db.String, nullable=True)
