import os
import json
from dotenv import load_dotenv
from pathlib import Path
import google.generativeai as genai

# Load .env from backend root directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("WARNING: GEMINI_API_KEY not found in .env file")
else:
    genai.configure(api_key=api_key)

def generate_questionnaire(resume_json, jd_json):
    """
    Generates structured interview questions using Gemini 2.0.
    Returns VALID JSON only.
    """

    prompt = f"""You are an interview question generator. Your output MUST be strictly valid JSON.
Do NOT include explanations. Do NOT include Markdown fences. DO NOT say "Sure, here is the JSON:".
JUST RETURN JSON.

RESUME DATA:
{json.dumps(resume_json, indent=2, ensure_ascii=False)}

JOB DESCRIPTION DATA:
{json.dumps(jd_json, indent=2, ensure_ascii=False)}

Generate interview questions following EXACTLY this JSON structure:

{{
  "project_questions": [
    {{
      "question": "string",
      "suggested_answer": "string",
      "keywords": ["string"]
    }}
  ],
  "resume_technical_questions": [
    {{
      "question": "string",
      "suggested_answer": "string",
      "keywords": ["string"]
    }}
  ],
  "jd_technical_questions": [
    {{
      "question": "string",
      "suggested_answer": "string",
      "keywords": ["string"]
    }}
  ],
  "experience_questions": [
    {{
      "question": "string",
      "suggested_answer": "string",
      "keywords": ["string"]
    }}
  ],
  "certificate_questions": [
    {{
      "question": "string",
      "suggested_answer": "string",
      "keywords": ["string"]
    }}
  ]
}}

RULES:
- Generate 3 project questions based on resume projects
- Generate 3 resume technical questions based on candidate's skills
- Generate 3 JD technical questions based on job requirements
- Generate 3 experience questions (only if experience exists in resume)
- Generate 2 certificate questions (only if certificates exist in resume)
- EVERY question MUST include:
    - A clear, specific question string
    - suggested_answer: A brief model answer or key points to look for (2-3 sentences)
    - 5-10 keywords (relevant technical terms or concepts)

Return ONLY the JSON object, no other text."""

    try:
        # Use Gemini 2.5 Flash (same as other utilities)
        model = genai.GenerativeModel("gemini-2.5-flash")

        # Generate content
        response = model.generate_content(prompt)

        raw_text = response.text.strip()

        # Remove markdown fences and extra text
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()

        # Extract JSON reliably
        start = cleaned.find("{")
        end = cleaned.rfind("}")

        if start == -1 or end == -1:
            raise ValueError("No JSON object found in response")

        clean_json = cleaned[start:end+1]

        parsed_json = json.loads(clean_json)
        
        # Validate structure
        required_keys = ["project_questions", "resume_technical_questions", 
                        "jd_technical_questions", "experience_questions", 
                        "certificate_questions"]
        
        for key in required_keys:
            if key not in parsed_json:
                parsed_json[key] = []
        
        return parsed_json

    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse JSON from Gemini response",
            "details": str(e),
            "raw": raw_text if 'raw_text' in locals() else "No output"
        }
    except Exception as e:
        return {
            "error": "Failed to generate interview questions",
            "details": str(e),
            "raw": raw_text if 'raw_text' in locals() else "No output"
        }
