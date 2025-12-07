"""
Recruitment Routes - Integrated with AI Backend
Uses AI Backend (Gemini) for resume parsing, JD generation, and ranking
"""
from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import db, Job, Applicant, Resume, Employee, User, Policy, Department
import os
import json
from datetime import datetime
from utils.ai_resume_parser import parse_resume_with_gpt
from utils.ai_jd_generator import build_prompt, generate_structured_jd
from utils.document_generator import generate_policy_document
from utils.ai_ranking import score_with_gemini
from utils.ai_questionnaire import generate_questionnaire
# from utils.ai_helpers import generate_structured_jd, generate_policy_document
UPLOAD_FOLDER = "uploads/resumes"
ALLOWED_EXTENSIONS = {"pdf", "docx"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class ResumeUpload(Resource):
    """Upload and parse resumes using AI Backend"""
    
    @jwt_required()
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user:
                return {"error": "User not found"}, 404

            job_id = request.form.get('job_id')
            
            # Check for duplicate application immediately
            existing_applicant = Applicant.query.filter_by(user_id=user.user_id, job_id=job_id).first()
            if existing_applicant:
                return {
                    "status": "error",
                    "message": "You have already applied for this position."
                }, 409

            # Fetch job details for filename
            job_title = "job"
            job_description = ""
            if job_id:
                job = Job.query.get(job_id)
                if job:
                    job_title = secure_filename(job.title)
                    job_description = job.jd_text
            
            files = request.files.getlist("files[]")
            results = []
            
            for file in files:
                if file and allowed_file(file.filename):
                    # Rename file: candidate-name_job-post-name_resume.ext
                    original_ext = file.filename.rsplit(".", 1)[1].lower()
                    safe_candidate_name = secure_filename(user.name)
                    new_filename = f"{safe_candidate_name}_{job_title}_resume.{original_ext}"
                    filepath = os.path.join(UPLOAD_FOLDER, new_filename)
                    file.save(filepath)
                    
                    # Parse with AI
                    parsed_dict = parse_resume_with_gpt(filepath)
                    
                    if 'error' not in parsed_dict:
                        try:
                            # Extract candidate info from nested structure
                            personal_info = parsed_dict.get('personal_info', {})
                            
                            # Flatten the structure for easier frontend consumption
                            flattened_parsed_data = {
                                'name': user.name,
                                'email': user.email,
                                'phone': personal_info.get('phone', ''),
                                'location': personal_info.get('location', ''),
                                'linkedin': personal_info.get('linkedin', ''),
                                'github': personal_info.get('github', ''),
                                'summary': parsed_dict.get('summary', ''),
                                'skills': parsed_dict.get('skills', []),
                                'experience': parsed_dict.get('experience', []),
                                'education': parsed_dict.get('education', []),
                                'certifications': parsed_dict.get('certifications', []),
                                'projects': parsed_dict.get('projects', []),
                                'raw_text': parsed_dict.get('raw_text', '')
                            }

                            # Create applicant record
                            applicant = Applicant(
                                user_id=user.user_id,
                                job_id=int(job_id),
                                status='Applied'
                            )
                            db.session.add(applicant)
                            db.session.flush()
                            
                            # Calculate Ranking Score immediately
                            ranking_score = 0
                            if job_description and flattened_parsed_data.get('raw_text'):
                                try:
                                    scores = score_with_gemini(job_title, job_description, flattened_parsed_data.get('raw_text'))
                                    ranking_score = scores.get('overall', 0)
                                except Exception as e:
                                    print(f"Ranking error: {e}")
                            
                            # Save score to applicant
                            applicant.score = ranking_score

                            # Save resume to database
                            resume = Resume(
                                applicant_id=applicant.applicant_id,
                                file_url=filepath,
                                parsed_text=flattened_parsed_data.get('raw_text', ''),
                                extracted_skills=json.dumps(flattened_parsed_data.get('skills', [])),
                                extracted_experience=json.dumps(flattened_parsed_data.get('experience', [])),
                                contact_info=json.dumps({
                                    'email': user.email,
                                    'phone': flattened_parsed_data.get('phone', ''),
                                    'location': flattened_parsed_data.get('location', '')
                                })
                            )
                            db.session.add(resume)
                            db.session.flush()
                            resume_id = resume.resume_id
                            
                            db.session.commit()

                            results.append({
                                "filename": new_filename,
                                "status": "success",
                                "parsed_data": flattened_parsed_data,
                                "resume_id": resume_id,
                                "applicant_id": applicant.applicant_id,
                                "ranking_score": ranking_score
                            })
                        except Exception as db_error:
                            db.session.rollback()
                            results.append({
                                "filename": filename,
                                "status": "error",
                                "error": f"Database error: {str(db_error)}"
                            })
                    else:
                        results.append({
                            "filename": filename,
                            "status": "error",
                            "error": parsed_dict.get('error', 'Parsing failed')
                        })
            
            return {
                "message": f"Processed {len(results)} files",
                "results": results
            }, 200
            
        except Exception as e:
            return {"error": f"Upload failed: {str(e)}"}, 500


class ResumeParseAdvanced(Resource):
    """Advanced resume parsing with database storage"""
    
    def post(self):
        try:
            if "file" not in request.files:
                return {"error": "No file uploaded"}, 400
            
            file = request.files["file"]
            if not file or not allowed_file(file.filename):
                return {"error": "Invalid file type"}, 400
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Parse with AI
            parsed_dict = parse_resume_with_gpt(filepath)
            
            if 'error' in parsed_dict:
                return {"error": parsed_dict['error']}, 500
            
            # Save to database
            try:
                # Extract candidate info
                candidate_name = parsed_dict.get('name', 'Unknown')
                candidate_email = parsed_dict.get('email', f"{filename.split('.')[0]}@temp.com")
                
                # Create or get user
                from models import User, Applicant
                user = User.query.filter_by(email=candidate_email).first()
                if not user:
                    user = User(
                        name=candidate_name,
                        email=candidate_email,
                        role='applicant'
                    )
                    user.set_password('temp123')  # Temporary password
                    db.session.add(user)
                    db.session.flush()
                
                # Create applicant record
                applicant = Applicant.query.filter_by(user_id=user.user_id).first()
                if not applicant:
                    # Get job_id from request if provided
                    job_id = request.form.get('job_id', None)
                    if job_id:
                        applicant = Applicant(
                            user_id=user.user_id,
                            job_id=int(job_id),
                            status='Applied'
                        )
                        db.session.add(applicant)
                        db.session.flush()
                
                # Save resume to database
                resume_id = None
                if applicant:
                    resume = Resume.query.filter_by(applicant_id=applicant.applicant_id).first()
                    if not resume:
                        resume = Resume(
                            applicant_id=applicant.applicant_id,
                            file_url=filepath,
                            parsed_text=parsed_dict.get('raw_text', ''),
                            extracted_skills=json.dumps(parsed_dict.get('skills', [])),
                            extracted_experience=json.dumps(parsed_dict.get('experience', [])),
                            contact_info=json.dumps({
                                'email': parsed_dict.get('email', ''),
                                'phone': parsed_dict.get('phone', ''),
                                'location': parsed_dict.get('location', '')
                            })
                        )
                        db.session.add(resume)
                        db.session.flush()
                        resume_id = resume.resume_id
                    else:
                        # Update existing resume
                        resume.file_url = filepath
                        resume.parsed_text = parsed_dict.get('raw_text', '')
                        resume.extracted_skills = json.dumps(parsed_dict.get('skills', []))
                        resume.extracted_experience = json.dumps(parsed_dict.get('experience', []))
                        resume.contact_info = json.dumps({
                            'email': parsed_dict.get('email', ''),
                            'phone': parsed_dict.get('phone', ''),
                            'location': parsed_dict.get('location', '')
                        })
                        resume_id = resume.resume_id
                
                db.session.commit()
                
                return {
                    "message": "Resume parsed successfully",
                    "parsed_resume": parsed_dict,
                    "resume_id": resume_id,
                    "applicant_id": applicant.applicant_id if applicant else None
                }, 200
                
            except Exception as db_error:
                db.session.rollback()
                # Still return parsed data even if DB save fails
                return {
                    "message": "Resume parsed but not saved to database",
                    "parsed_resume": parsed_dict,
                    "resume_id": None,
                    "warning": f"Database error: {str(db_error)}"
                }, 200
                
        except Exception as e:
            return {"error": f"Parse failed: {str(e)}"}, 500


class CandidateJobMatcher(Resource):

    def post(self):
        try:
            data = request.get_json() or {}

            job_description = data.get("job_description", "").strip()
            job_title = data.get("job_title", "Unknown Role")

            if not job_description:
                return {"error": "job_description is required"}, 400

            # Fetch employees with parsed resumes
            employees = Employee.query.filter(Employee.parsed_resume.isnot(None)).all()
            print(f"DEBUG: Found {len(employees)} employees with parsed resumes")

            if not employees:
                print("DEBUG: No employees with resumes found, returning empty rankings")
                return {
                    "message": "Candidate matching complete",
                    "total_candidates": 0,
                    "rankings": []
                }, 200

            rankings = []

            for employee in employees:
                try:
                    print(f"DEBUG: Processing employee {employee.emp_id} - {employee.user.name if employee.user else 'Unknown'}")
                    # Get parsed resume text
                    resume_text = employee.parsed_resume or ""

                    # Score using Gemini
                    print(f"DEBUG: Calling score_with_gemini for employee {employee.emp_id}")
                    scores = score_with_gemini(job_title, job_description, resume_text)
                    print(f"DEBUG: Received scores for employee {employee.emp_id}: {scores}")

                    if scores:
                        rankings.append({
                            "emp_id": employee.emp_id,
                            "name": employee.user.name if employee.user else "Unknown",
                            "email": employee.user.email if employee.user else None,
                            "job_title": employee.job_title,
                            "department": employee.department.name if employee.department else None,
                            "skills": employee.get_skills(),
                            "experience_years": employee.experience_years,
                            **scores
                        })
                        print(f"DEBUG: Added employee {employee.emp_id} to rankings")
                    else:
                        print(f"DEBUG: No scores returned for employee {employee.emp_id}")

                except Exception as e:
                    print(f"ERROR scoring employee {employee.emp_id}: {str(e)}")
                    import traceback
                    traceback.print_exc()

            rankings_sorted = sorted(rankings, key=lambda x: x.get("overall", 0), reverse=True)
            print(f"DEBUG: Returning {len(rankings_sorted)} ranked candidates")
            print(f"DEBUG: Rankings data: {rankings_sorted[:2] if rankings_sorted else 'empty'}")

            return {
                "message": "Candidate matching complete",
                "job_title": job_title,
                "total_candidates": len(rankings_sorted),
                "rankings": rankings_sorted
            }, 200

        except Exception as e:
            return {"error": "Unexpected server error", "details": str(e)}, 500




class InterviewQuestionGenerator(Resource):
    """Generate interview questions using AI"""

    def post(self):
        try:
            data = request.get_json() or {}

            resume_id = data.get("resume_id")
            job_id = data.get("job_id") or data.get("job_description_id")
            applicant_id = data.get("applicant_id")
            
            # If applicant_id provided, fetch resume_id and job_id from it
            if applicant_id and not (resume_id and job_id):
                applicant = Applicant.query.get(applicant_id)
                if applicant:
                    resume_id = applicant.resume.resume_id if applicant.resume else None
                    job_id = applicant.job_id

            candidate_name = data.get("candidate_name", "")
            skills = data.get("skills", [])
            job_description = data.get("job_description", "")

            # --------------------------
            # Case 1: Use DB records
            # --------------------------
            if resume_id and job_id:
                resume = Resume.query.get(resume_id)
                job = Job.query.get(job_id)

                if not resume:
                    return {"error": "Resume not found"}, 404
                if not job:
                    return {"error": "Job description not found"}, 404

                # Check if questions already exist
                applicant = resume.applicant
                if applicant and applicant.interview_questions:
                    try:
                        saved_questions = json.loads(applicant.interview_questions)
                        return {
                            "message": "Interview questions retrieved from database",
                            "resume_id": resume_id,
                            "job_id": job_id,
                            "questions": saved_questions
                        }, 200
                    except:
                        pass # If JSON parse fails, regenerate

                # Build resume JSON from Resume model fields
                resume_json = {
                    "name": resume.applicant.user.name if resume.applicant and resume.applicant.user else "Unknown",
                    "email": resume.get_contact_info().get('email', ''),
                    "phone": resume.get_contact_info().get('phone', ''),
                    "skills": resume.get_skills(),
                    "experience": resume.get_experience(),
                    "raw_text": resume.parsed_text or ""
                }

                # Build job JSON from Job model fields
                job_json = {
                    "title": job.title,
                    "description": job.jd_text or "",
                    "requirements": job.get_requirements(),
                    "location": job.location,
                    "employment_type": job.employment_type
                }

                questions = generate_questionnaire(resume_json, job_json)
                
                # Save to database
                if applicant:
                    applicant.interview_questions = json.dumps(questions)
                    # Update status to Screening if it's currently Applied
                    if applicant.status == 'Applied':
                        applicant.status = 'Screening'
                    db.session.commit()

                return {
                    "message": "Interview questions generated and saved",
                    "resume_id": resume_id,
                    "job_id": job_id,
                    "questions": questions
                }, 200

            # --------------------------
            # Case 2: Direct frontend input
            # --------------------------
            elif job_description or skills:
                resume_data = {
                    "name": candidate_name,
                    "skills": skills if isinstance(skills, list) else []
                }

                job_data = {
                    "description": job_description
                }

                questions = generate_questionnaire(resume_data, job_data)

                return {
                    "message": "Interview questions generated",
                    "questions": questions
                }, 200

            # --------------------------
            # No valid inputs
            # --------------------------
            else:
                return {
                    "error": "Provide resume_id & job_id OR candidate_name/skills & job_description"
                }, 400

        except Exception as e:
            import traceback
            return {
                "error": "Failed to generate interview questions",
                "details": str(e),
                "traceback": traceback.format_exc()
            }, 500



def normalize_ai_response(structured, data):
    """
    Normalize AI response to expected flat structure.
    Handles both old nested format and new flat format.
    """
    # Check if it's already in the new flat format
    if 'role_summary' in structured and 'minimum_qualifications' in structured:
        return structured
    
    # Otherwise, transform from old/mixed format
    role_def = structured.get('role_definition', {})
    
    # Infer responsibilities if empty
    responsibilities = structured.get('responsibilities', [])
    if not responsibilities:
        job_title = data.get('jobTitle', '')
        seniority = data.get('seniority', '')
        # Generate default responsibilities based on role
        if 'front' in job_title.lower() or 'ui' in job_title.lower():
            responsibilities = [
                "Design and implement responsive user interfaces using modern frameworks",
                "Collaborate with designers and backend engineers to deliver seamless user experiences",
                "Write clean, maintainable, and well-tested code",
                "Optimize applications for maximum speed and scalability",
                "Participate in code reviews and contribute to team knowledge sharing",
                "Stay up-to-date with emerging trends and technologies in frontend development"
            ]
        else:
            responsibilities = [
                "Design and develop high-quality software solutions",
                "Collaborate with cross-functional teams to define and ship new features",
                "Write clean, efficient, and maintainable code",
                "Participate in code reviews and technical discussions",
                "Contribute to continuous improvement of development processes"
            ]
    
    # Infer minimum qualifications
    min_quals = structured.get('minimum_qualifications', [])
    must_have = structured.get('must_have_skills', [])
    if not min_quals:
        min_quals = [
            f"Bachelor's degree in Computer Science, related field, or equivalent practical experience",
            f"{data.get('minExperience', '3')}+ years of professional experience in software development"
        ]
        # Add skills from must_have_skills or mustHaveSkills
        #for skill in must_have or data.get('mustHaveSkills', []):
        #min_quals.append(f"Proficiency in {skill}")
        min_quals.extend([
            "Strong problem-solving and analytical skills",
            "Excellent communication and collaboration abilities"
        ])
    
    # Infer preferred qualifications
    pref_quals = structured.get('preferred_qualifications', [])
    nice_to_have = structured.get('nice_to_have_skills', [])
    if not pref_quals:
        pref_quals = []
        #for skill in nice_to_have or data.get('niceToHaveSkills', []):
        #   pref_quals.append(f"Experience with {skill}")
        if not pref_quals:
            pref_quals = [
                "Experience in fast-paced startup environments",
                "Contributions to open-source projects",
                "Strong portfolio demonstrating technical excellence"
            ]
    
    # Build role summary
    role_summary = structured.get('role_summary', '')
    if not role_summary:
        summary = role_def.get('Summary', '') or structured.get('structured_text', '')
        mission = role_def.get('Mission', '') or data.get('coreMission', '')
        role_summary = f"{summary} {mission}".strip()
        if not role_summary:
            role_summary = f"Join {data.get('companyName', 'our team')} as a {data.get('jobTitle', 'team member')} where you'll have the opportunity to make a meaningful impact. This {data.get('seniority', '')} role offers the chance to work on innovative solutions while growing your career in a dynamic environment."
    
    # Build about_team
    about_team = structured.get('about_team', '')
    if not about_team:
        company_blurb = data.get('companyBlurb', '')
        company_name = data.get('companyName', 'Our company')
        field = data.get('field', 'technology')
        about_team = f"{company_name} {company_blurb} We're a team of passionate professionals in the {field} industry, committed to innovation and excellence. You'll collaborate with talented individuals who value creativity, continuous learning, and delivering exceptional results."
    
    # Normalize benefits
    benefits = structured.get('benefits', data.get('benefits', []))
    
    return {
        'job_title': role_def.get('Job_Title', data.get('jobTitle', '')),
        'company_name': data.get('companyName', ''),
        'location': data.get('location', ''),
        'employment_type': data.get('employmentType', ''),
        'salary_range': data.get('salaryRange', ''),
        'role_summary': role_summary,
        'responsibilities': responsibilities,
        'minimum_qualifications': min_quals,
        'preferred_qualifications': pref_quals,
        'about_team': about_team,
        'benefits': benefits
    }


class GenerateJobPosting(Resource):

    def post(self):
        try:
            data = request.get_json()
            print(f"DEBUG: GenerateJobPosting received data: {data}")
            
            # Validate ONLY essential fields
            required_fields = ['jobTitle']  # Only job title is truly required
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                return {"error": f"Missing required fields: {', '.join(missing)}"}, 400
            
            # Set intelligent defaults for optional fields
            data.setdefault('companyName', 'Acme Inc')
            data.setdefault('minExperience', '2-3')
            data.setdefault('location', 'Hybrid')
            data.setdefault('city', '')
            data.setdefault('employmentType', 'Full-time')
            data.setdefault('salaryRange', 'Competitive')
            data.setdefault('tone', 'Professional')
            data.setdefault('field', 'E-Commerce')
            data.setdefault('companySize', '120')
            data.setdefault('quantity', 1)
            
            # Set company context defaults
            data.setdefault('coreMission', 
                "To revolutionize the e-commerce experience by delivering seamless, personalized shopping journeys that connect millions of customers with the products they love. We leverage cutting-edge technology and data-driven insights to build the future of online retail.")
            data.setdefault('companyBlurb',
                "Acme is a leading e-commerce platform transforming how people discover, evaluate, and purchase products online. With a customer-obsessed culture and commitment to innovation, we operate at the intersection of technology, logistics, and retail to deliver exceptional experiences at scale. Our diverse, world-class team is building solutions that shape the future of commerce for millions of users worldwide.")
            data.setdefault('benefits', [
                "Competitive Compensation with Equity & Performance Bonuses",
                "Comprehensive Health & Wellness Benefits",
                "Flexible Work Options & Generous Time Off",
                "Career Growth with Learning & Development Support",
                "Direct Impact on Millions of Customers Worldwide",
                "Cutting-Edge Technology & Innovation-Driven Culture"
            ])
                
        except Exception as e:
            return {"error": f"Invalid JSON: {str(e)}"}, 400

        # Call AI generator with structured data (PASS THE DICT, NOT TEXT)
        structured = generate_structured_jd(data)
        
        if "error" in structured:
            return {"error": structured["error"]}, 500

        # Normalize AI response to expected structure
        try:
            normalized = normalize_ai_response(structured, data)
        except Exception as e:
            return {"error": f"Failed to normalize AI response: {str(e)}"}, 500

        # Build HTML output
        try:
            html_output = self._build_html_output(normalized)
        except Exception as e:
            return {"error": f"Failed to build HTML: {str(e)}"}, 500

        # Save to database or Update existing
        try:
            job_id = data.get('job_id')
            
            if job_id:
                job = Job.query.get(job_id)
                if not job:
                    return {"error": f"Job ID {job_id} not found"}, 404
                    
                # Update existing job
                self._update_job(job, data, html_output, normalized)
                db.session.commit()
                
                return {
                    "message": "Job updated successfully",
                    "html": html_output,
                    "job_id": job.job_id,
                    "structured_jd": structured
                }, 200
            
            # Create new job
            new_job = self._create_job(data, html_output, normalized)
            db.session.add(new_job)
            db.session.commit()
            
            return {
                "message": "Job posting generated and saved",
                "structured_jd": structured,
                "html": html_output,
                "job_id": new_job.job_id
            }, 200
            
        except Exception as e:
            db.session.rollback()
            print(f"Error saving job to DB: {e}")
            return {"error": f"Database error: {str(e)}"}, 500

    # KEEP ALL YOUR EXISTING HELPER METHODS - THEY'RE GOOD!
    def _build_html_output(self, normalized):
        """Build HTML from normalized job data"""
        return f"""
<div class="job-posting">
    <h1>{normalized['job_title']}</h1>
    <h2>{normalized['company_name']}</h2>
    
    <div class="job-meta">
        <p><strong>Location:</strong> {normalized['location']}</p>
        <p><strong>Type:</strong> {normalized['employment_type']}</p>
        <p><strong>Salary:</strong> {normalized['salary_range']}</p>
    </div>

    <hr/>

    <h3>The Role</h3>
    <p>{normalized['role_summary']}</p>

    <h3>Key Responsibilities</h3>
    <ul>{''.join(f'<li>{item}</li>' for item in normalized['responsibilities'])}</ul>

    <h3>Minimum Qualifications</h3>
    <ul>{''.join(f'<li>{item}</li>' for item in normalized['minimum_qualifications'])}</ul>

    <h3>Preferred Qualifications</h3>
    <ul>{''.join(f'<li>{item}</li>' for item in normalized['preferred_qualifications'])}</ul>

    <h3>About the Team</h3>
    <p>{normalized['about_team']}</p>

    <h3>Benefits</h3>
    <ul>{''.join(f'<li>{item}</li>' for item in normalized['benefits'])}</ul>
</div>
"""

    def _update_job(self, job, data, html_output, normalized):
        """Update existing job with new data"""
        job.title = normalized.get('job_title', data.get('jobTitle', 'Untitled Role'))
        job.jd_text = html_output
        job.requirements = json.dumps(data.get('mustHaveSkills', []))
        job.location = normalized.get('location', data.get('location', ''))
        job.employment_type = normalized.get('employment_type', data.get('employmentType', ''))
        job.salary_range = normalized.get('salary_range', data.get('salaryRange', ''))
        job.quantity = int(data.get('quantity') or 1)
        job.input_data = json.dumps(data)
        
        # Only update status if explicitly provided
        if 'status' in data:
            job.status = data['status']
        
        # Update department if changed
        if 'field' in data or 'jobTitle' in data:
            job.dept_id = self._determine_department(data)

    def _create_job(self, data, html_output, normalized):
        """Create new job instance"""
        return Job(
            title=normalized.get('job_title', data.get('jobTitle', 'Untitled Role')),
            jd_text=html_output,
            requirements=json.dumps(data.get('mustHaveSkills', [])),
            status=data.get('status', 'Draft'),
            location=normalized.get('location', data.get('location', '')),
            employment_type=normalized.get('employment_type', data.get('employmentType', '')),
            salary_range=normalized.get('salary_range', data.get('salaryRange', '')),
            quantity=int(data.get('quantity') or 1),
            input_data=json.dumps(data),
            posted_date=datetime.utcnow(),
            dept_id=self._determine_department(data)
        )

    def _determine_department(self, data):
        """
        Determine department based on job data.
        Returns department ID or None.
        """
        field = data.get('field', '').lower()
        title = data.get('jobTitle', '').lower()
        
        # Define department mapping
        DEPT_MAPPING = {
            'engineering': ['engineer', 'developer', 'architect', 'devops', 'sre', 'tech lead', 'software'],
            'product': ['product manager', 'product owner', 'apm', 'assistant product'],
            'operations': ['operations', 'ops coordinator', 'supply chain', 'logistics'],
            'design': ['designer', 'ux', 'ui', 'creative'],
            'marketing': ['marketing', 'growth', 'content', 'seo', 'social media'],
            'sales': ['sales', 'account executive', 'business development'],
            'hr': ['hr', 'recruiter', 'talent', 'people ops'],
            'finance': ['finance', 'accounting', 'analyst'],
            'customer_success': ['customer success', 'support', 'account manager']
        }
        
        # Try to find department from database by name
        for dept_name, keywords in DEPT_MAPPING.items():
            if any(keyword in title or keyword in field for keyword in keywords):
                dept = Department.query.filter_by(name=dept_name.replace('_', ' ').title()).first()
                if dept:
                    return dept.dept_id
        
        # Return None if no match found
        return None

class GeneratePolicyDocument(Resource):

    def post(self):
        data = request.get_json()

        location = data.get("location", "")
        requirements = data.get("requirements", "")

        policy_data = generate_policy_document(location, requirements)
        
        # Save to database
        new_policy = Policy(
            title=policy_data.get('title', 'Generated Policy'),
            content=policy_data.get('content', ''),
            category='General', # Default category
            created_at=datetime.utcnow()
        )
        db.session.add(new_policy)
        db.session.commit()

        return {
            "message": "Policy document generated and saved",
            "document": policy_data.get('content', ''),
            "policy_id": new_policy.policy_id,
            "title": new_policy.title,
            "category": new_policy.category
        }, 200


class PolicyList(Resource):
    def get(self):
        try:
            policies = Policy.query.order_by(Policy.created_at.desc()).all()
            return {
                "policies": [p.to_dict() for p in policies]
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500


class PolicyLocations(Resource):
    def get(self):
        return {
            "locations": [
                "canada", "usa", "uk", "australia", "india",
                "germany", "france", "singapore", "uae"
            ]
        }, 200


class WritingTones(Resource):
    def get(self):
        return {
            "tones": [
                "Professional", "Friendly", "Formal",
                "Startup-friendly", "Creative", "Technical"
            ]
        }, 200


class JobListResource(Resource):
    @jwt_required(optional=True)
    def get(self):
        try:
            current_user_id = get_jwt_identity()
            applied_job_ids = set()
            
            if current_user_id:
                # Get list of job_ids this user has applied for
                applications = Applicant.query.filter_by(user_id=current_user_id).all()
                applied_job_ids = {app.job_id for app in applications}
                application_status_map = {app.job_id: app.status for app in applications}

            jobs = Job.query.order_by(Job.created_at.desc()).all()
            
            job_list = []
            for job in jobs:
                job_dict = job.to_dict()
                job_dict['has_applied'] = job.job_id in applied_job_ids
                job_dict['application_status'] = application_status_map.get(job.job_id) if current_user_id else None
                job_list.append(job_dict)

            return {
                "jobs": job_list
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500


class JobDetailResource(Resource):
    def put(self, job_id):
        try:
            job = Job.query.get(job_id)
            if not job:
                return {"error": "Job not found"}, 404
            
            data = request.get_json()
            
            # Update fields if provided
            if 'jd_text' in data:
                job.jd_text = data['jd_text']
            
            if 'status' in data:
                new_status = data['status']
                if new_status in ['Draft', 'On Hold', 'Open', 'Closed']:
                    job.status = new_status
            
            if 'title' in data:
                job.title = data['title']
                
            if 'location' in data:
                job.location = data['location']
                
            if 'salary_range' in data:
                job.salary_range = data['salary_range']

            db.session.commit()
            
            return {
                "message": "Job updated successfully",
                "job_id": job.job_id,
                "status": job.status
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500

    def delete(self, job_id):
        try:
            job = Job.query.get(job_id)
            if not job:
                return {"error": "Job not found"}, 404
            
            db.session.delete(job)
            db.session.commit()
            
            return {"message": "Job deleted successfully"}, 200
        except Exception as e:
            return {"error": str(e)}, 500


class UpdateJobStatus(Resource):
    def put(self, job_id):
        try:
            job = Job.query.get(job_id)
            if not job:
                return {"error": "Job not found"}, 404
            
            data = request.get_json()
            new_status = data.get('status')
            
            if new_status not in ['Draft', 'On Hold', 'Open', 'Closed']:
                return {"error": "Invalid status"}, 400
            
            job.status = new_status
            db.session.commit()
            
            return {"message": f"Job status updated to {new_status}", "job_id": job.job_id}, 200
        except Exception as e:
            return {"error": str(e)}, 500


class FinalizeJob(Resource):
    def post(self, job_id):
        try:
            job = Job.query.get(job_id)
            if not job:
                return {"error": "Job not found"}, 404
            
            job.status = 'On Hold'
            db.session.commit()
            
            return {"message": "Job finalized (On Hold)", "job_id": job.job_id}, 200
        except Exception as e:
            return {"error": str(e)}, 500


class PostJob(Resource):
    def post(self, job_id):
        try:
            job = Job.query.get(job_id)
            if not job:
                return {"error": "Job not found"}, 404
            
            job.status = 'Open'
            db.session.commit()
            
            return {"message": "Job posted successfully", "job_id": job.job_id}, 200
        except Exception as e:
            return {"error": str(e)}, 500


class JobApplicants(Resource):
    def get(self, job_id):
        try:
            job = Job.query.get(job_id)
            if not job:
                return {"error": "Job not found"}, 404
            
            # Explicitly join to ensure we get user details
            # Use outer join for resume in case it's missing (though it shouldn't be)
            applicants = db.session.query(Applicant, User, Resume)\
                .join(User, Applicant.user_id == User.user_id)\
                .outerjoin(Resume, Applicant.applicant_id == Resume.applicant_id)\
                .filter(Applicant.job_id == job_id)\
                .all()
            
            results = []
            
            for applicant, user, resume in applicants:
                score = applicant.score if applicant.score is not None else 0
                
                # Fallback: if score is 0 and resume exists, try to calculate it
                if score == 0 and resume and resume.parsed_text:
                     try:
                        scores = score_with_gemini(job.title, job.jd_text, resume.parsed_text)
                        score = scores.get('overall', 0)
                        applicant.score = score
                        db.session.commit()
                     except:
                        pass

                results.append({
                    "applicant_id": applicant.applicant_id,
                    "name": user.name,
                    "email": user.email,
                    "status": applicant.status,
                    "score": score,
                    "resume_url": f"/api/{resume.file_url}" if resume and resume.file_url else None,
                    "summary": (resume.parsed_text[:200] + "...") if resume and resume.parsed_text else "",
                    "q_and_a_scores": json.loads(applicant.q_and_a_scores) if applicant.q_and_a_scores else []
                })
            
            # Sort by score descending
            results.sort(key=lambda x: x['score'], reverse=True)
            
            return {"applicants": results}, 200
        except Exception as e:
            return {"error": str(e)}, 500
class SaveApplicantScores(Resource):
    """Save manual interview scores for an applicant"""
    @jwt_required()
    def post(self, applicant_id):
        try:
            data = request.get_json()
            scores = data.get('scores', [])
            
            if not isinstance(scores, list):
                return {"error": "Scores must be a list"}, 400
                
            # Validate scores
            validated_scores = []
            for score in scores:
                try:
                    s = float(score)
                    if s < 0 or s > 10:
                        return {"error": "All scores must be between 0 and 10"}, 400
                    validated_scores.append(s)
                except ValueError:
                    return {"error": "Invalid score format"}, 400
            
            applicant = Applicant.query.get(applicant_id)
            if not applicant:
                return {"error": "Applicant not found"}, 404
                
            # Save scores as JSON to q_and_a_scores
            applicant.q_and_a_scores = json.dumps(validated_scores)
            
            # Do NOT update overall score (applicant.score) as it represents the AI Match Score
            # The Interview Score will be calculated on the frontend from q_and_a_scores
            
            # Update status to Interview
            applicant.status = 'Interview'
            
            db.session.commit()
            
            return {
                "message": "Scores saved successfully",
                "applicant": applicant.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500


class HireRejectApplicantResource(Resource):
    """Hire or Reject an applicant"""
    @jwt_required()
    def post(self, applicant_id):
        try:
            data = request.get_json()
            status = data.get('status')
            
            if status not in ['Hired', 'Rejected']:
                return {"error": "Invalid status. Must be 'Hired' or 'Rejected'"}, 400
                
            applicant = Applicant.query.get(applicant_id)
            if not applicant:
                return {"error": "Applicant not found"}, 404
                
            applicant.status = status
            db.session.commit()
            
            return {
                "message": f"Applicant marked as {status}",
                "applicant_id": applicant.applicant_id,
                "status": applicant.status
            }, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500
