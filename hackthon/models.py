from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False) # 'hr' or 'candidate'
    
class CandidateProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pseudo_id = db.Column(db.String(50), unique=True, nullable=False)
    skills = db.Column(db.Text, nullable=False, default='[]') # stored as JSON string
    experience_level = db.Column(db.String(50), nullable=False) # 'fresher' or 'experienced'
    experience_years = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref=db.backref('profile', uselist=False))

    def get_skills_list(self):
        try:
            return json.loads(self.skills)
        except:
            return []

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    skills = db.Column(db.Text, nullable=False, default='[]') # required skills as JSON
    salary_range = db.Column(db.String(100))
    target_level = db.Column(db.String(50), nullable=False) # 'fresher' or 'experienced'
    status = db.Column(db.String(50), default='active') # 'active' or 'closed'
    
    hr = db.relationship('User', backref=db.backref('jobs', lazy=True))

    def get_skills_list(self):
        try:
            return json.loads(self.skills)
        except:
            return []

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profile.id'), nullable=False)
    profile_score = db.Column(db.Float, default=0.0)
    test_score = db.Column(db.Float, default=0.0)
    total_score = db.Column(db.Float, default=0.0)
    warnings = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='applied') # 'applied', 'testing', 'completed'
    
    job = db.relationship('Job', backref=db.backref('applications', lazy=True))
    candidate = db.relationship('CandidateProfile', backref=db.backref('applications', lazy=True))
