import os
import random
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json

from models import db, User, CandidateProfile, Job, Application
from scoring import generate_job_description, calculate_profile_score, calculate_total_score

app = Flask(__name__)
app.config['SECRET_KEY'] = 'space_antigravity_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///antigravity.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_dummy_data():
    if User.query.first():
        return
    # Create HR
    hr_user = User(email='hr@antigravity.com', password_hash=generate_password_hash('password'), role='hr')
    db.session.add(hr_user)
    db.session.commit()
    
    # Create Job
    job = Job(
        hr_id=hr_user.id,
        title='Senior Backend Engineer',
        description=generate_job_description('Senior Backend Engineer', ['python', 'flask', 'sql'], 'experienced', '$120k - $150k'),
        skills=json.dumps(['python', 'flask', 'sql']),
        salary_range='$120k - $150k',
        target_level='experienced'
    )
    db.session.add(job)
    db.session.commit()
    
    # Create Candidates
    candidate_skills = [
        ['python', 'flask', 'sql'],
        ['python', 'django', 'aws'],
        ['java', 'sql'],
        ['python', 'flask', 'sql', 'docker']
    ]
    for i, skills in enumerate(candidate_skills):
        user = User(email=f'candidate{i+1}@test.com', password_hash=generate_password_hash('password'), role='candidate')
        db.session.add(user)
        db.session.commit()
        
        profile = CandidateProfile(
            user_id=user.id,
            pseudo_id=f"Candidate-{i+100}",
            skills=json.dumps(skills),
            experience_level='experienced',
            experience_years=5
        )
        db.session.add(profile)
        db.session.commit()
        
        # apply
        prof_score = calculate_profile_score(profile.skills, job.skills, profile.experience_level, job.target_level)
        app_record = Application(
            job_id=job.id,
            candidate_id=profile.id,
            profile_score=prof_score,
            test_score=random.randint(60, 100),
            status='completed'
        )
        app_record.total_score = calculate_total_score(app_record.profile_score, app_record.test_score)
        db.session.add(app_record)
        
    db.session.commit()

with app.app_context():
    db.create_all()
    create_dummy_data()

# -----------------
# Auth Routes
# -----------------
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'hr':
            return redirect(url_for('hr_dashboard'))
        return redirect(url_for('candidate_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role == 'hr':
                return redirect(url_for('hr_dashboard'))
            return redirect(url_for('candidate_dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
            
        user = User(email=email, password_hash=generate_password_hash(password), role=role)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        if role == 'candidate':
            return redirect(url_for('candidate_profile'))
        return redirect(url_for('hr_dashboard'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# -----------------
# HR Routes
# -----------------
def hr_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'hr':
            flash("Unauthorized access", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/hr/dashboard')
@hr_required
def hr_dashboard():
    jobs = Job.query.filter_by(hr_id=current_user.id).all()
    return render_template('hr_dashboard.html', jobs=jobs)

@app.route('/hr/post-job', methods=['GET', 'POST'])
@hr_required
def post_job():
    if request.method == 'POST':
        title = request.form.get('title')
        skills_raw = request.form.get('skills')
        salary = request.form.get('salary')
        level = request.form.get('level')
        
        skills_list = [s.strip().lower() for s in skills_raw.split(',') if s.strip()]
        description = generate_job_description(title, skills_list, level, salary)
        
        job = Job(
            hr_id=current_user.id,
            title=title,
            skills=json.dumps(skills_list),
            salary_range=salary,
            target_level=level,
            description=description
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('hr_dashboard'))
    return render_template('post_job.html')

@app.route('/hr/job/<int:id>')
@hr_required
def job_details(id):
    job = Job.query.get_or_404(id)
    if job.hr_id != current_user.id:
        return "Unauthorized", 403
        
    # Get top 5 candidates based on total_score
    applications = Application.query.filter_by(job_id=job.id).order_by(Application.total_score.desc()).limit(5).all()
    return render_template('job_details.html', job=job, applications=applications)

# -----------------
# Candidate Routes
# -----------------
def candidate_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'candidate':
            flash("Unauthorized access", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/candidate/dashboard')
@candidate_required
def candidate_dashboard():
    profile = CandidateProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        return redirect(url_for('candidate_profile'))
        
    all_jobs = Job.query.filter_by(status='active').all()
    my_applications = {app.job_id: app for app in Application.query.filter_by(candidate_id=profile.id).all()}
    
    return render_template('candidate_dashboard.html', jobs=all_jobs, applications=my_applications, profile=profile)

@app.route('/candidate/profile', methods=['GET', 'POST'])
@candidate_required
def candidate_profile():
    profile = CandidateProfile.query.filter_by(user_id=current_user.id).first()
    if request.method == 'POST':
        skills_raw = request.form.get('skills')
        skills_list = [s.strip().lower() for s in skills_raw.split(',') if s.strip()]
        level = request.form.get('level')
        years = request.form.get('years', 0)
        
        if not profile:
            count = CandidateProfile.query.count()
            profile = CandidateProfile(
                user_id=current_user.id,
                pseudo_id=f"Candidate-{count+1000}",
                skills=json.dumps(skills_list),
                experience_level=level,
                experience_years=int(years)
            )
            db.session.add(profile)
        else:
            profile.skills = json.dumps(skills_list)
            profile.experience_level = level
            profile.experience_years = int(years)
            
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('candidate_dashboard'))
        
    skills_str = ", ".join(json.loads(profile.skills)) if profile else ""
    return render_template('candidate_profile.html', profile=profile, skills_str=skills_str)

@app.route('/candidate/apply/<int:job_id>', methods=['POST'])
@candidate_required
def apply_job(job_id):
    profile = CandidateProfile.query.filter_by(user_id=current_user.id).first()
    job = Job.query.get_or_404(job_id)
    
    if Application.query.filter_by(job_id=job.id, candidate_id=profile.id).first():
        flash('Already applied', 'error')
        return redirect(url_for('candidate_dashboard'))
        
    prof_score = calculate_profile_score(profile.skills, job.skills, profile.experience_level, job.target_level)
    
    application = Application(
        job_id=job.id,
        candidate_id=profile.id,
        profile_score=prof_score,
        status='testing'
    )
    db.session.add(application)
    db.session.commit()
    
    return redirect(url_for('test_portal', application_id=application.id))

@app.route('/candidate/test/<int:application_id>')
@candidate_required
def test_portal(application_id):
    application = Application.query.get_or_404(application_id)
    profile = CandidateProfile.query.filter_by(user_id=current_user.id).first()
    if application.candidate_id != profile.id:
        return "Unauthorized", 403
    if application.status == 'completed':
        flash('Test already submitted', 'error')
        return redirect(url_for('candidate_dashboard'))
        
    return render_template('test_portal.html', application=application)

@app.route('/candidate/test/<int:application_id>/submit', methods=['POST'])
@candidate_required
def submit_test(application_id):
    application = Application.query.get_or_404(application_id)
    # mock checking answers (random logic for demo)
    score = random.randint(60, 100)
    warnings = int(request.form.get('warnings', 0))
    if warnings >= 3:
        score = 0 # automatic fail for cheating
        
    application.test_score = score
    application.total_score = calculate_total_score(application.profile_score, score)
    application.warnings = warnings
    application.status = 'completed'
    db.session.commit()
    
    flash('Test submitted successfully!', 'success')
    return redirect(url_for('candidate_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
