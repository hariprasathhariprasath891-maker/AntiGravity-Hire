import json

def generate_job_description(title, skills_list, level, salary):
    skills_str = ", ".join(skills_list)
    desc = f"<h3>Job Overview</h3>\n"
    desc += f"<p>We are looking for an outstanding <strong>{title}</strong> to join our fast-paced, space-bound team. "
    if level == 'fresher':
        desc += "This is an entry-level position perfect for bright minds looking to start their true journey into the galaxy of code."
    else:
        desc += "This role requires seasoned experience to navigate complex technical challenges and lead mission-critical projects."
        
    desc += f"</p>\n<h3>Key Requirements</h3>\n"
    desc += f"<ul>\n<li>Proficiency in the following areas: <strong>{skills_str}</strong>.</li>\n"
    desc += f"<li>Experience level requirement: <strong>{level.capitalize()}</strong>.</li>\n"
    desc += f"<li>Strong analytical and problem-solving abilities.</li>\n</ul>\n"
    
    if salary:
        desc += f"<h3>Compensation</h3>\n<p>Salary Range: <strong>{salary}</strong></p>\n"
        
    desc += "<div class='jd-footer'><em>AntiGravity Hire ensures all evaluations are strictly merit-based. Bias is left at the door. Your code speaks for you.</em></div>"
    return desc

def calculate_profile_score(candidate_skills_str, job_skills_str, candidate_exp_level, job_level):
    try:
        candidate_skills = [s.strip().lower() for s in json.loads(candidate_skills_str)]
    except:
        candidate_skills = []
        
    try:
        job_skills = [s.strip().lower() for s in json.loads(job_skills_str)]
    except:
        job_skills = []

    if not job_skills:
        return 50.0 
        
    matched = set(candidate_skills).intersection(set(job_skills))
    
    skill_score = (len(matched) / len(job_skills)) * 100.0 if job_skills else 0.0
    
    level_score = 100.0 if candidate_exp_level.lower() == job_level.lower() else 30.0
    
    # 70% weight to skills, 30% to level match
    final_score = (skill_score * 0.70) + (level_score * 0.30)
    return round(final_score, 2)

def calculate_total_score(profile_score, test_score):
    # 40% profile match, 60% actual test performance
    return round((profile_score * 0.40) + (test_score * 0.60), 2)
