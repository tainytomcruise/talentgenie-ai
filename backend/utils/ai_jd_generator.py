import os
import json
from datetime import datetime
from pathlib import Path
from flask import session 
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------------- ENV ---------------------- #
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# ---------------------- HELPER ---------------------- #
def sanitize_dict(obj):
    """Remove any non-serializable objects from dict"""
    if isinstance(obj, dict):
        return {k: sanitize_dict(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_dict(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # Convert non-serializable objects to string
        return str(obj)

# ======================================================
# PROMPT
# ======================================================
def build_prompt(user_data: dict) -> str:
    """
    Minimal input prompt - AI infers everything else intelligently
    """
    job_title = user_data.get('jobTitle', 'Software Engineer')
    experience = user_data.get('minExperience', '2-3')
    location = user_data.get('location', 'Remote')
    city = user_data.get('city', '')
    salary = user_data.get('salaryRange', 'Competitive')
    specific_skills = user_data.get('mustHaveSkills', [])
    special_requirements = user_data.get('specialRequirements', '')
    tone = user_data.get('tone', 'Professional')
    
    # Company defaults
    company_name = user_data.get('companyName', 'Acme Inc')
    company_mission = """To revolutionize the e-commerce experience by delivering seamless, personalized shopping journeys that connect millions of customers with the products they love. We leverage cutting-edge technology and data-driven insights to build the future of online retail."""
    company_blurb = """Acme is a leading e-commerce platform transforming how people discover, evaluate, and purchase products online. With a customer-obsessed culture and commitment to innovation, we operate at the intersection of technology, logistics, and retail to deliver exceptional experiences at scale. Our diverse, world-class team is building solutions that shape the future of commerce for millions of users worldwide."""
    
    benefits = [
        "Competitive Compensation with Equity & Performance Bonuses",
        "Comprehensive Health & Wellness Benefits",
        "Flexible Work Options & Generous Time Off",
        "Career Growth with Learning & Development Support",
        "Direct Impact on Millions of Customers Worldwide",
        "Cutting-Edge Technology & Innovation-Driven Culture"
    ]
    
    full_location = f"{city}, {location}" if city else location
    skills_text = ", ".join(specific_skills) if specific_skills else "none specified"
    
    return f"""
You are an elite MAANG-level HR content strategist. Generate a world-class job description from MINIMAL input.

CRITICAL: Output ONLY valid JSON. No markdown, no code blocks, no extra text.

USER PROVIDED (MINIMAL INPUT):
- Job Title: {job_title}
- Experience Level: {experience} years
- Location: {full_location}
- Salary Range: {salary}
- Specific Skills Requested: {skills_text}
- Special Requirements: {special_requirements or "None"}
- Desired Tone: {tone}

COMPANY CONTEXT (USE THIS):
- Company: {company_name}
- Mission: {company_mission}
- About: {company_blurb}
- Benefits: {chr(10).join(f"  - {b}" for b in benefits)}

YOUR TASK:
You must INTELLIGENTLY INFER everything else based on:
1. **Job Title** → Determine role type, responsibilities, required skills, tools
2. **Experience Level** → Determine seniority, qualification depth, leadership expectations
3. **Industry** (E-commerce) → Tailor examples, metrics, domain knowledge

INTELLIGENCE RULES:

1. **Infer Seniority from Experience:**
   - 0-1 years → Entry-Level/Intern
   - 1-3 years → Junior/Associate
   - 3-5 years → Mid-Level
   - 5-8 years → Senior
   - 8+ years → Staff/Principal/Lead

2. **Infer Role Category from Title:**
   - "Engineer", "Developer" → Technical role (mention languages, frameworks, architecture)
   - "Product Manager", "APM" → Product role (mention user research, roadmaps, metrics)
   - "Designer" → Design role (mention Figma, user flows, prototyping)
   - "Operations", "Coordinator" → Ops role (mention process optimization, tools, coordination)
   - "Marketing" → Marketing role (mention campaigns, analytics, growth)

3. **Infer Responsibilities Based on Role + Seniority:**
   - Junior: Individual contributor tasks, learning, execution
   - Mid: Ownership of features, collaboration, some mentoring
   - Senior: Architecture, leadership, strategy, mentoring teams

4. **Infer Required Tools/Technologies:**
   - Software Engineers → Programming languages, frameworks, databases, cloud platforms
   - Product Managers → Jira/Linear, Figma, Analytics tools, SQL (basic)
   - Designers → Figma/Sketch, prototyping tools, design systems
   - Operations → Excel/Sheets, project management tools, ERP systems
   - If user specified skills, PRIORITIZE those but add complementary ones

5. **Infer Qualifications Based on Experience:**
   - Entry: Degree or bootcamp, foundational skills, enthusiasm
   - Mid: Degree + relevant experience, proven track record, specific achievements
   - Senior: Advanced degree (preferred), extensive experience, leadership examples

6. **Write Industry-Specific Content:**
   - E-commerce roles → Mention: conversion rates, user journeys, personalization, scale (millions of users), checkout flows, recommendations
   - Use relevant metrics and terminology for the domain

7. **Match Tone:**
   - Professional → Formal, structured, traditional corporate language
   - Startup-friendly → Casual "we" language, emphasize impact and learning
   - Innovative → Emphasize cutting-edge tech, experimentation, pushing boundaries

REQUIRED OUTPUT STRUCTURE:
{{
  "job_title": "Properly formatted title with seniority if needed",
  "company_name": "{company_name}",
  "location": "{full_location}",
  "employment_type": "Full-time",
  "salary_range": "{salary}",
  "role_summary": "3-4 compelling sentences connecting role to company mission, highlighting impact and growth",
  "responsibilities": [
    "6-8 specific, outcome-focused responsibilities with technologies, metrics, and business impact",
    "Format: Action verb + specific task + technology/tool + measurable outcome"
  ],
  "minimum_qualifications": [
    "5-7 qualifications combining education, experience, skills, and achievements",
    "Inferred from experience level and role type",
    "Include specific tools if user mentioned them"
  ],
  "preferred_qualifications": [
    "4-6 qualifications that define excellence in this role",
    "Certifications, advanced skills, domain expertise, leadership examples"
  ],
  "about_team": "Vivid paragraph describing team mission, tech stack, culture, work style, and what makes team unique. Mention specific technologies and methodologies. Paint a picture of day-to-day work.",
  "benefits": {json.dumps(benefits)}
}}

QUALITY STANDARDS (CRITICAL):
✅ Responsibilities must mention SPECIFIC technologies, tools, and measurable outcomes
✅ Qualifications must tell a story, not just list requirements
✅ About team must be vivid with real details, not generic platitudes
✅ NEVER use "Proficiency in X" without context
✅ NEVER leave arrays empty - infer appropriate content
✅ NEVER be generic - use specific e-commerce examples

EXAMPLE FOR "Assistant Product Manager, 2-3 years":

{{
  "job_title": "Assistant Product Manager",
  "company_name": "Acme Inc",
  "location": "Bangalore, India (Hybrid)",
  "employment_type": "Full-time",
  "salary_range": "$85,000 - $125,000",
  "role_summary": "Join Acme's product team to drive features that impact millions of shoppers daily. As an Assistant Product Manager, you'll collaborate with engineering, design, and data science to build and optimize our e-commerce platform—from personalized recommendations to seamless checkout experiences. This role offers direct exposure to product strategy, user research, and data-driven decision making while working alongside experienced PMs who will mentor your growth into a senior product leader.",
  "responsibilities": [
    "Partner with senior PMs to define feature requirements and write detailed user stories for shopping cart, checkout, and product discovery features",
    "Conduct user interviews and analyze session recordings using Hotjar to identify friction points in the purchase journey and propose UX improvements",
    "Create and maintain product analytics dashboards in Mixpanel tracking key metrics like conversion rate, cart abandonment, and time-to-purchase",
    "Coordinate sprint planning and daily standups with engineering teams using Jira, ensuring alignment on priorities and delivery timelines",
    "Run A/B tests on product pages and analyze results to make data-driven recommendations for feature iterations",
    "Document product specifications and user flows in Notion, ensuring clear communication across design, engineering, and QA teams",
    "Present weekly product performance reports to stakeholders, highlighting wins, blockers, and insights from customer feedback"
  ],
  "minimum_qualifications": [
    "Bachelor's degree in Business, Computer Science, Engineering, or related field, or equivalent practical experience in product roles",
    "2-3 years of experience in product management, business analysis, consulting, or related role in tech or e-commerce companies",
    "Demonstrated ability to write clear user stories, acceptance criteria, and product requirements documents (PRDs)",
    "Strong analytical skills with proficiency in tools like Excel/Google Sheets for data analysis and basic SQL for querying databases",
    "Experience working cross-functionally with engineering, design, and business teams in agile/scrum environments",
    "Excellent communication skills with ability to present complex ideas clearly to both technical and non-technical audiences",
    "Data-driven mindset with experience using analytics tools like Google Analytics, Mixpanel, Amplitude, or similar platforms"
  ],
  "preferred_qualifications": [
    "Experience with product management tools like Jira, Linear, Productboard, or Aha! for roadmap planning and backlog management",
    "Familiarity with A/B testing frameworks and experimentation platforms like Optimizely, VWO, or LaunchDarkly",
    "Previous experience in e-commerce, marketplace, or consumer-facing products with understanding of user purchase behavior",
    "Basic understanding of UX/UI design principles with experience using Figma for collaborating with designers",
    "Technical background or ability to understand APIs, database structures, and system architecture discussions",
    "MBA or advanced degree in a related field with coursework in product management or business strategy"
  ],
  "about_team": "You'll join Acme's Core Shopping Experience team, a cross-functional squad of 2 product managers, 6 engineers, 2 designers, and 1 data analyst building the product pages, cart, and checkout flows that drive $50M+ in annual GMV. We ship features bi-weekly using agile sprints, run 10+ A/B tests monthly, and maintain a modern tech stack including React, Node.js, PostgreSQL, and AWS. Your PM mentor will guide your growth through weekly 1-on-1s, involve you in strategic planning sessions, and give you ownership of key metrics like cart conversion rate. Our hybrid schedule includes Tuesdays and Thursdays in our Bangalore office for design reviews and sprint planning, with flexible remote work other days. Expect a collaborative culture where junior voices are valued, learning is prioritized through lunch-and-learns, and we celebrate shipping features that measurably improve customer experience.",
  "benefits": {json.dumps(benefits)}
}}

NOW GENERATE THE JOB DESCRIPTION. Think deeply about the role type, experience level, and industry context. Output ONLY the JSON object.
"""

# ======================================================
# GEMINI CALL
# ======================================================
def generate_structured_jd(user_data: dict) -> dict:  # ← Changed from str to dict
    """
    Generate structured job description using Gemini.
    user_data should be a dict with all the form fields.
    Returns a dict - NEVER returns Response objects.
    """
    if not user_data or not isinstance(user_data, dict):
        return {
            "error": "Invalid input data format. Please provide a dictionary with job details.",
            "structured_text": ""
        }

    response_text = ""
    try:
        prompt = build_prompt(user_data)
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        gemini_response = model.generate_content(prompt)
        
        # CRITICAL: Extract text immediately and discard response object
        try:
            response_text = str(gemini_response.text).strip()
        except AttributeError:
            return {
                "error": "Gemini response has no text attribute",
                "structured_text": str(user_data)
            }
        except Exception as text_error:
            return {
                "error": f"Failed to extract text: {str(text_error)}",
                "structured_text": str(user_data)
            }
        
        # At this point, gemini_response should be garbage collected
        # We only work with response_text (string) from here
        del gemini_response  # Explicitly delete to ensure it's not referenced
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        try:
            json_output = json.loads(response_text)
            
            # Double-check: ensure it's a plain dict with only serializable types
            if not isinstance(json_output, dict):
                return {
                    "error": "Gemini returned non-dict response",
                    "structured_text": str(user_data)
                }
            
            # Sanitize to ensure no Response objects are included
            clean_output = sanitize_dict(json_output)
            
            # Final safety check - try to serialize it
            print(f"DEBUG: About to return type: {type(clean_output)}")
            print(f"DEBUG: Keys in output: {list(clean_output.keys()) if isinstance(clean_output, dict) else 'Not a dict'}")
            try:
                json.dumps(clean_output)  # Test serialization
            except TypeError as serialize_error:
                return {
                    "error": f"Output contains non-serializable data: {str(serialize_error)}",
                    "structured_text": str(user_data)
                }
            
            return clean_output
            
        except json.JSONDecodeError as json_error:
            return {
                "error": f"Failed to parse JSON: {str(json_error)}",
                "structured_text": str(user_data),
                "raw_response": response_text[:500] if response_text else "No response"
            }

    except Exception as e:
        return {
            "error": f"Gemini API error: {str(e)}",
            "structured_text": str(user_data)
        }


# ======================================================
# SESSION HELPERS
# ======================================================
def _get_temp_data():
    return session.get("temp_jd_input"), session.get("temp_jd_structured")

def _set_temp_data(input_text, structured_output):
    session["temp_jd_input"] = input_text
    session["temp_jd_structured"] = structured_output

def _clear_temp_data():
    session.pop("temp_jd_input", None)
    session.pop("temp_jd_structured", None)


# ======================================================
# ROUTE HANDLERS USED IN app.py
# ======================================================
def handle_jd_submission(request):
    data = request.get_json(silent=True) or {}
    jd_text = data.get("jd_text", "").strip()

    if not jd_text:
        return {"error": "JD text not provided"}, 400

    structured = generate_structured_jd(jd_text)

    _set_temp_data(jd_text, structured)

    return {
        "message": "Structured JD generated successfully",
        "structured_jd": structured
    }


def handle_jd_update(request):
    data = request.get_json(silent=True) or {}
    update_text = data.get("update_text", "").strip()

    if not update_text:
        return {"error": "Update text not provided"}, 400

    prev_text, _ = _get_temp_data()
    if not prev_text:
        return {"error": "No JD found. Please submit first."}, 400

    merged_text = prev_text + "\n\nUPDATE REQUEST:\n" + update_text
    structured = generate_structured_jd(merged_text)

    _set_temp_data(merged_text, structured)

    return {
        "message": "JD updated successfully",
        "structured_jd": structured
    }


def handle_jd_confirmation(request):
    original_text, structured = _get_temp_data()
    if not structured:
        return {"error": "Nothing to confirm"}, 400

    data = request.get_json(silent=True) or {}

    # -------------------------
    # AUTO-EXTRACT JOB TITLE
    # -------------------------
    auto_title = structured.get("job_title")

    # -------------------------
    # SAFE TITLE LOGIC (fix)
    # -------------------------
    incoming_title = data.get("position", "").strip()

    if incoming_title and incoming_title != "Auto-generated JD":
        position = incoming_title
    else:
        position = auto_title or "Untitled Position"

    position = position.strip()

    location = data.get("location", "Not specified")
    status_value = RecruitmentStatus.in_progress.value

    # Construct JD JSON from flat structure
    jd_json = {
        "role_definition": {
            "Job_Title": structured.get("job_title", ""),
            "Seniority_Level": data.get("seniority", ""), # Fallback to input data
            "Core_Mission": structured.get("role_summary", ""),
            "Primary_Objectives": structured.get("responsibilities", [])
        },
        "candidate_profile": {
            "Minimum_Years_of_Experience": data.get("minExperience", ""),
            "Must_Have_Skills_Qualifications": structured.get("minimum_qualifications", []),
            "Nice_to_Have_Skills": structured.get("preferred_qualifications", []),
            "Required_Tools_Software": []
        },
        "company_team_context": {
            "Company_Name": structured.get("company_name", ""),
            "Company_Blurb": structured.get("about_team", ""),
            "Field_Industry": data.get("field", ""),
            "Company_Type_Size": data.get("companySize", ""),
            "Team_Reporting_Structure": data.get("teamStructure", "")
        },
        "logistics_style": {
            "Work_Location": structured.get("location", ""),
            "Employment_Type": structured.get("employment_type", ""),
            "Salary_Range": structured.get("salary_range", ""),
            "Key_Benefits": structured.get("benefits", []),
            "Application_Instructions": "",
            "Tone": data.get("tone", "")
        }
    }

    final_text = structured.get("structured_text", "")

    new_jd = JobDescription(
        Recrutement_position=position,
        location=location,
        status=RecruitmentStatus(status_value),
        JD_details_json=json.dumps(jd_json, ensure_ascii=False, indent=2),
        structured_jd=final_text,
        drive_start_date=datetime.utcnow(),
    )

    db.session.add(new_jd)
    db.session.commit()

    _clear_temp_data()

    return {"message": "JD saved successfully", "jd_id": new_jd.id}


def fetch_all_jds():
    records = JobDescription.query.all()
    result = []
    for jd in records:
        result.append({
            "id": jd.id,
            "title": jd.Recrutement_position,
            "position": jd.Recrutement_position,
            "location": jd.location,
            "status": jd.status.value,
            "JD_details_json": json.loads(jd.JD_details_json or "{}"),
            "structured_jd": jd.structured_jd,
            "created_at": jd.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
    return result
