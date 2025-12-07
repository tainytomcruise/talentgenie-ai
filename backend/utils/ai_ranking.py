import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
import google.generativeai as genai

from models import db
from models import Resume


# --------------------------------------------------------------
# Load ENV + Configure Gemini
# --------------------------------------------------------------
load_dotenv(Path(__file__).parent / ".env", override=True)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# --------------------------------------------------------------
# Utility: Convert to float (0–10)
# --------------------------------------------------------------
def _to_score(v: Any) -> Optional[float]:
    try:
        n = float(v)
        if n < 0:
            n = 0.0
        if n > 100:
            n = 100.0
        return round(n, 2)
    except:
        return None


# --------------------------------------------------------------
# Gemini AI Scoring
# --------------------------------------------------------------
def score_with_gemini(job_title: str, jd_text: str, resume_text: str) -> Optional[Dict[str, float]]:
    """
    Sends resume + job description to Gemini and returns structured scoring.
    """

    prompt = f"""
You are an expert technical recruiter for the role "{job_title}".

JOB DESCRIPTION:
\"\"\"{jd_text}\"\"\"


RESUME:
\"\"\"{resume_text}\"\"\"


Evaluate the resume on a strict scale of **0–100** for these metrics:

1. technical_skills
2. experience_relevance
3. impact
4. communication
5. education

Return STRICT JSON ONLY:
{{
  "technical_skills": <0-100>,
  "experience_relevance": <0-100>,
  "impact": <0-100>,
  "communication": <0-100>,
  "education": <0-100>,
  "overall": <0-100>
}}
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        # Check if response exists and has text
        if not response or not hasattr(response, 'text'):
            print("⚠️ Gemini scoring error: No response from API")
            return None

        raw = response.text.strip()

        # Check if response is empty
        if not raw:
            print("⚠️ Gemini scoring error: Empty response from API")
            return None

        # Extract JSON only
        start = raw.find("{")
        end = raw.rfind("}")

        if start == -1 or end == -1:
            print(f"⚠️ Gemini scoring error: No JSON found in response. Raw response: {raw[:200]}")
            return None

        json_str = raw[start:end + 1]
        data = json.loads(json_str)

        tech = _to_score(data.get("technical_skills"))
        exp = _to_score(data.get("experience_relevance"))
        imp = _to_score(data.get("impact"))
        comm = _to_score(data.get("communication"))
        edu = _to_score(data.get("education"))
        overall = _to_score(data.get("overall"))

        # If overall missing → compute average
        if overall is None:
            vals = [v for v in [tech, exp, imp, comm, edu] if v is not None]
            overall = round(sum(vals) / len(vals), 2) if vals else 0.0

        return {
            "technical_skills": tech,
            "experience_relevance": exp,
            "impact": imp,
            "communication": comm,
            "education": edu,
            "overall": overall
        }

    except json.JSONDecodeError as e:
        print(f"⚠️ Gemini scoring JSON error: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Gemini scoring error: {e}")
        return None


# --------------------------------------------------------------
# MAIN: Score ALL resumes for a dynamic job description
# --------------------------------------------------------------
def score_all_resumes(job_title: str, job_description: str):
    """
    Called by your CandidateJobMatcher controller.
    Returns a list of scored + sorted candidates.
    """

    resumes = Resume.query.all()

    if not resumes:
        return []

    results = []

    for resume in resumes:
        try:
            # Actual resume text field according to your model
            resume_text = resume.parsed_text or ""

            scores = score_with_gemini(job_title, job_description, resume_text)

            if scores:
                results.append({
                    "resume_id": resume.resume_id,
                    "applicant_id": resume.applicant_id,
                    "resume_name": (
                        resume.applicant.user.name
                        if resume.applicant and resume.applicant.user
                        else None
                    ),
                    **scores
                })

        except Exception as e:
            print("Error scoring a resume:", e)

    # Sort by overall descending
    results_sorted = sorted(results, key=lambda x: x["overall"], reverse=True)

    return results_sorted
