from frontend import db
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Создаем экземпляр declarative_base (sqlalchemy)


class RepositoryInfo(Base):
    __tablename__ = 'repo_info'
    id = Column(Integer, primary_key=True)
    upd_date = Column(DateTime, onupdate=func.now(), default=func.now(), nullable=False)
    repo_path = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    stars = Column(Integer, nullable=False)
    version = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)
    pushed_at = Column(Integer, nullable=False)
    archived = Column(Boolean, nullable=False)
    locked = Column(Boolean, nullable=False)
    issues_count = Column(Integer, nullable=False)
    bug_issues_count = Column(Integer, nullable=False)
    bug_issues_closed_count = Column(Integer, nullable=False)
    bug_issues_open_count = Column(Integer, nullable=False)
    watchers_count = Column(Integer, nullable=False)
    fork_count = Column(Integer, nullable=False)
    closed_bug_95perc = Column(Integer, nullable=True)
    closed_bug_50perc = Column(Integer, nullable=True)
    upd_major_ver = Column(Integer, nullable=True)
    upd_minor_ver = Column(Integer, nullable=True)
    upd_patch_ver = Column(Integer, nullable=True)
    bug_issues_no_comment = Column(Float, nullable=True)
    bug_issues_closed2m = Column(Float, nullable=True)
    pr_closed_count2m = Column(Integer, nullable=True)
    pr_closed_duration = Column(Float, nullable=True)
    time = Column(Float, nullable=False)
    cost = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<{self.repo_path}>'


class QueryStatistics(Base):
    __tablename__ = 'query_stat'
    id = Column(Integer, primary_key=True)
    crt_date = Column(DateTime, default=func.now(), nullable=False)
    repo_path = Column(String, nullable=False)
    issues_count = Column(Integer, nullable=False)
    bug_issues_count = Column(Integer, nullable=False)
    time = Column(Float, nullable=False)
    cost = Column(Integer, nullable=False)
    request_kf = Column(Float, nullable=False)
    query_limit = Column(Integer, nullable=True)
    estimated_time = Column(Float, nullable=True)
    request_downtime = Column(Float, nullable=False)


class RepositoryCollection(Base):
    __tablename__ = 'repo_collection'
    id = Column(Integer, primary_key=True)
    crt_date = Column(DateTime, default=func.now(), nullable=False)
    repo_path = Column(String, unique=True, nullable=False)
    token_hash = Column(String, nullable=False)
    saved = Column(Boolean, default=False, nullable=False)


Base.metadata.create_all(db)  # Создаем все таблицы
