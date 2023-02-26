from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app import db
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy import Column, DateTime, func

Base = declarative_base()





class RepositoryInfo(Base):
    __tablename__ = 'repository_info'
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
    bug_issues_closed_2months = Column(Float, nullable=True)
    pr_closed_count = Column(Integer, nullable=True)
    pr_closed_duration = Column(Float, nullable=True)
    time = Column(Float, nullable=False)
    cost = Column(Integer, nullable=False)

    def __repr__(self):
        return f'<{self.repo_path}>'

    @staticmethod
    def create_database_table():
        Base.metadata.create_all(db)


class QueryStatistics(Base):
    __tablename__ = 'quer_statistics'
    id = Column(Integer, primary_key=True)
    crt_date = Column(DateTime, default=func.now(), nullable=False)
    repo_path = Column(String, nullable=False)
    issues_count = Column(Integer, nullable=False)
    bug_issues_count = Column(Integer, nullable=False)
    time = Column(Float, nullable=False)
    cost = Column(Integer, nullable=False)
    request_kf = Column(Float, nullable=False)
    query_limit = Column(Integer, nullable=True)
    rt = Column(String, nullable=True)

    @staticmethod
    def create_database_table():
        Base.metadata.create_all(db)


class RepositoryCollection(Base):
    __tablename__ = 'repository_collection'
    id = Column(Integer, primary_key=True)
    crt_date = Column(DateTime, default=func.now(), nullable=False)
    repo_path = Column(String, unique=True, nullable=False)
    token_hash = Column(String, nullable=False)
    saved = Column(Boolean, default=False, nullable=False)

    @staticmethod
    def create_database_table():
        Base.metadata.create_all(db)

