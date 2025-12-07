from app_modular import app
from models import db, User, Job, Applicant, Resume

with app.app_context():
    print("--- USERS (Specific) ---")
    users = User.query.filter(User.user_id.in_([161, 163])).all()
    for u in users:
        print(f"ID: {u.user_id}, Name: {u.name}, Email: {u.email}, Role: {u.role}")

    print("\n--- JOBS (Last 10) ---")
    jobs = Job.query.all()[-10:]
    for j in jobs:
        print(f"ID: {j.job_id}, Title: {j.title}, Status: {j.status}")

    print("\n--- APPLICANTS (Last 10) ---")
    applicants = Applicant.query.all()[-10:]
    for a in applicants:
        print(f"AppID: {a.applicant_id}, UserID: {a.user_id}, JobID: {a.job_id}, Status: {a.status}, Score: {a.score}")
        
    print("\n--- RESUMES (Last 10) ---")
    resumes = Resume.query.all()[-10:]
    for r in resumes:
        print(f"ResumeID: {r.resume_id}, AppID: {r.applicant_id}, File: {r.file_url}")
