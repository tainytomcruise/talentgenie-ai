# ai_helpers.py
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def _extract_json_from_text(text: str):
    """
    Extract JSON from messy LLM output.
    """

    # 1. Remove backticks (```json ... ``` format)
    text = text.replace("```json", "").replace("```", "").strip()

    # 2. Try direct JSON load
    try:
        return json.loads(text)
    except:
        pass

    # 3. Try extracting JSON substring
    match = re.search(r"{[\s\S]*}", text)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except:
            pass

    # 4. Try using a lenient JSON fixer
    try:
        fixed = text.replace("\n", "")
        fixed = re.sub(r",\s*}", "}", fixed)  # remove trailing comma before }
        fixed = re.sub(r",\s*]", "]", fixed)  # remove trailing comma before ]
        return json.loads(fixed)
    except:
        return None



# -----------------------------
# 1. Generate Structured Job Posting
# -----------------------------
def generate_structured_jd(jd_text: str) -> dict:
    prompt = f"""
You are an expert HR recruiter.

Rewrite and structure the following job posting into clean, well-organized sections.

Return ONLY valid JSON with this structure:
{{
  "role_definition": {{
    "Job_Title": "",
    "Summary": "",
    "Mission": ""
  }},
  "responsibilities": [],
  "must_have_skills": [],
  "nice_to_have_skills": [],
  "tools": [],
  "benefits": [],
  "structured_text": ""
}}

Do NOT add any explanation.

RAW INPUT:
{jd_text}
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)

        raw_text = response.text

        # Extract and fix JSON
        parsed = _extract_json_from_text(raw_text)

        if parsed is None:
            return {
                "error": "Failed to parse AI JSON output",
                "raw_output": raw_text
            }

        return parsed

    except Exception as e:
        return {"error": f"Gemini generation failed: {str(e)}"}



# -----------------------------
# 2. Generate Policy Document
# -----------------------------
def generate_policy_document(location: str, requirements: str) -> dict:
    prompt = f"""
Generate a clean, professional HR policy document for location: {location}.
Focus area: {requirements}.
Tone: professional.

Return ONLY valid JSON with this structure:
{{
  "title": "A short, descriptive title for the policy",
  "content": "The full HTML content of the policy document (use <h2>, <p>, <ul>, <li> tags)"
}}
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        
        # Reuse the JSON extractor
        parsed = _extract_json_from_text(response.text)
        
        if parsed is None:
             # Fallback if JSON parsing fails
            return {
                "title": "Generated Policy",
                "content": response.text
            }
            
        return parsed

    except Exception as e:
        return {"title": "Error", "content": f"Policy generation failed: {str(e)}"}
