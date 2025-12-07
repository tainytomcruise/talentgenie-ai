"""
Document Generator using Google Gemini 2.5 Flash
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# Setup Gemini with validation
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)


def generate_reference_letter(employee_name: str, position: str, department: str, achievements: str) -> str:
    """
    Generate reference letter
    
    Args:
        employee_name: Employee's full name
        position: Job position
        department: Department name
        achievements: Key achievements
    
    Returns:
        Reference letter text
    """
    # Fallback template
    fallback_letter = f"""[Date: {datetime.now().strftime('%B %d, %Y')}]

To Whom It May Concern,

I am writing to provide a reference for {employee_name}, who has been working as a {position} in our {department} department.

{employee_name} has demonstrated exceptional skills and dedication during their tenure with our organization. {achievements}

I highly recommend {employee_name} for any position they may seek.

Sincerely,
[HR Manager]
[Company Name]
"""

    if not api_key:
        return fallback_letter

    prompt = f"""Generate a professional reference letter for:

Employee: {employee_name}
Position: {position}
Department: {department}
Key Achievements: {achievements}

The letter should:
- Be formal and professional
- Highlight the employee's strengths
- Mention specific achievements
- Be suitable for job applications
- Include standard reference letter structure

Format as a complete letter with date, salutation, body, and signature placeholder.
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        if not response or not hasattr(response, 'text'):
            print("⚠️ Reference letter: No response from API")
            return fallback_letter

        response_text = response.text.strip()

        if not response_text:
            print("⚠️ Reference letter: Empty response")
            return fallback_letter

        return response_text

    except Exception as e:
        print(f"⚠️ Reference letter error: {e}")
        return fallback_letter


def generate_employment_proof(employee_name: str, position: str, department: str, hire_date: str) -> str:
    """
    Generate employment verification letter
    
    Args:
        employee_name: Employee's full name
        position: Job position
        department: Department name
        hire_date: Date of hire
    
    Returns:
        Employment proof letter
    """
    current_date = datetime.now().strftime('%B %d, %Y')
    
    return f"""EMPLOYMENT VERIFICATION LETTER

Date: {current_date}

To Whom It May Concern,

This letter serves to verify that {employee_name} is currently employed with our organization.

Employee Details:
- Name: {employee_name}
- Position: {position}
- Department: {department}
- Employment Start Date: {hire_date}
- Employment Status: Active

This letter is issued upon the request of {employee_name} for official purposes.

If you require any additional information, please feel free to contact our Human Resources department.

Sincerely,

[HR Manager Name]
Human Resources Department
[Company Name]
[Contact Information]
"""


def generate_policy_document(location: str, requirements: str) -> str:
    """
    Generate policy document based on location and requirements

    Args:
        location: Country/region for compliance
        requirements: Specific policy requirements

    Returns:
        Policy document text
    """
    fallback_policy = f"""WORKPLACE POLICY DOCUMENT

Location: {location}
Effective Date: {datetime.now().strftime('%B %d, %Y')}

1. PURPOSE
This policy document outlines the workplace standards and practices for {location}.

2. SCOPE
This policy applies to all employees, contractors, and visitors.

3. REQUIREMENTS
{requirements}

4. COMPLIANCE
All staff members are expected to comply with this policy and applicable laws in {location}.

5. REVIEW
This policy will be reviewed annually and updated as necessary.

For questions or clarifications, please contact the Human Resources department.
"""

    if not api_key:
        return fallback_policy

    prompt = f"""Generate a comprehensive workplace policy document for:

Location: {location}
Requirements: {requirements}

The policy should:
- Be compliant with {location} labor laws
- Include clear sections (Purpose, Scope, Policy Details, Compliance, Review)
- Be professional and legally sound
- Address the specific requirements mentioned
- Include implementation guidelines

Format as a formal policy document.
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)

        if not response or not hasattr(response, 'text'):
            print("⚠️ Policy document: No response from API")
            return fallback_policy

        response_text = response.text.strip()

        if not response_text:
            print("⚠️ Policy document: Empty response")
            return fallback_policy

        return response_text

    except Exception as e:
        print(f"⚠️ Policy document error: {e}")
        return fallback_policy
