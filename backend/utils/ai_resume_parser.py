import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(override=True)

import json
import re
from PyPDF2 import PdfReader
import google.generativeai as genai
from utils.resume_schema import ResumeSchema

# Setup Gemini with validation
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

def clean_json_str(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text)
    text = re.sub(r"```$", "", text)
    text = text.replace(""", "\"").replace(""", "\"")
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # remove duplicate keys (like "certifications" repeated)
    text = re.sub(r'"certifications":\s*\[[^\]]*\]\s*,\s*"certifications":', '"certifications":', text)

    return text


def parse_resume_with_gpt(file_path: str):
    """Extracts resume text and parses structured data using Google Gemini 2.5 Flash."""

    # Check API key
    if not api_key:
        return {"error": "GEMINI_API_KEY not configured", "raw_text": ""}

    # Extract text
    try:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    except Exception as e:
        return {"error": f"Failed to read PDF: {str(e)}", "raw_text": ""}

    if not text.strip():
        return {"error": "Empty PDF or no text extracted", "raw_text": ""}

    # Create prompt for Gemini
    prompt = f"""You are an AI resume parser. Extract detailed structured information from the given resume text and return it strictly as JSON.

Resume text:
{text}

Return a JSON object with the following structure:
{{
    "personal_info": {{
        "name": "string",
        "email": "string",
        "phone": "string",
        "location": "string",
        "linkedin": "string (optional)",
        "github": "string (optional)"
    }},
    "summary": "string",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "company": "string",
            "position": "string",
            "duration": "string",
            "responsibilities": ["resp1", "resp2", ...]
        }}
    ],
    "education": [
        {{
            "institution": "string",
            "degree": "string",
            "field": "string",
            "year": "string"
        }}
    ],
    "certifications": ["cert1", "cert2", ...],
    "projects": [
        {{
            "name": "string",
            "description": "string",
            "technologies": ["tech1", "tech2", ...]
        }}
    ]
}}

Return ONLY the JSON object, no additional text."""

    try:
        # Run Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        # Validate response
        if not response or not hasattr(response, 'text'):
            print("⚠️ Gemini API returned no response")
            return {"error": "No response from Gemini API", "raw_text": text[:500]}

        raw_output = response.text.strip()

        if not raw_output:
            print("⚠️ Gemini API returned empty response")
            return {"error": "Empty response from Gemini API", "raw_text": text[:500]}

        cleaned = clean_json_str(raw_output)

        try:
            parsed_data = json.loads(cleaned)
            # Add raw_text for database storage
            parsed_data['raw_text'] = text
            return parsed_data
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parse failed: {e}")
            print(f"Raw output (first 500 chars): {raw_output[:500]}")
            return {"error": f"JSON parsing failed: {str(e)}", "raw_text": text[:500]}

    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return {"error": str(e), "raw_text": text[:500]}
