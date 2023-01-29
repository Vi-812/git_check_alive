# # from app import app_flask, db
# # from datetime import datetime
# # from sqlalchemy import Column, ForeignKey, Integer, String
#
#
# class RepositoryInfo(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     upd = db.Column(db.DateTime, nullable=False, onupdate=datetime.now)
#     name = db.Column(db.String, nullable=False)
#     owner_login = db.Column(db.String, nullable=False)  # unique=True
#     description = db.Column(db.String, nullable=False)
#     homepage_url = db.Column(db.String, nullable=True)
#     stars_count = db.Column(db.Integer, nullable=False)
#     version = db.Column(db.String, nullable=True)
#     created_at = db.Column(db.DateTime, nullable=False)
#     duration = db.Column(db.Integer, nullable=False)
#     updated_at = db.Column(db.Integer, nullable=False)
#     pushed_at = db.Column(db.Integer, nullable=False)
#     archived = db.Column(db.Boolean, nullable=False)
#     issues_count = db.Column(db.Integer, nullable=False)
#     bug_issues_count = db.Column(db.Integer, nullable=False)
#     bug_issues_closed_count = db.Column(db.Integer, nullable=False)
#     bug_issues_open_count = db.Column(db.Integer, nullable=False)
#     upd_major_ver = db.Column(db.Integer, nullable=True)
#     upd_minor_ver = db.Column(db.Integer, nullable=True)
#     upd_path_ver = db.Column(db.Integer, nullable=True)
#     pr_closed_count = db.Column(db.Integer, nullable=True)
#     pr_closed_duration = db.Column(db.Integer, nullable=True)
#     closed_bug_50percent = db.Column(db.Integer, nullable=True)
#     closed_bug_95percent = db.Column(db.Integer, nullable=True)
#     bug_issues_no_comment = db.Column(db.Float, nullable=True)
#     bug_issues_closed_two_months = db.Column(db.Float, nullable=True)
#     request_duration_time = db.Column(db.String, nullable=False)
#     request_total_cost = db.Column(db.Integer, nullable=False)
#     request_kf = db.Column(db.Float, nullable=False)
#
#
# with app_flask.app_context():
#     db.create_all()
