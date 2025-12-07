"""
Learning Path Generator using Google Gemini 2.5 Flash
"""
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# Setup Gemini with validation
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)


def generate_learning_path(current_role: str, career_goal: str, employee_id: int = None) -> dict:
    """
    Generate personalized learning path
    
    Args:
        current_role: Current job role
        career_goal: Desired career goal
        employee_id: Optional employee ID
    
    Returns:
        Learning path with modules
    """
    # Fallback learning path
    fallback_path = {
        "learning_path": {
            "title": f"Path from {current_role} to {career_goal}",
            "total_duration_weeks": 24,
            "modules": [
                {
                    "module_name": "1. Foundations",
                    "description": "Build core skills and understand fundamental concepts needed for your career transition.",
                    "duration_weeks": 4,
                    "key_topics": ["Basics", "Core concepts", "Best practices", "Industry standards"],
                    "prerequisites": ["Basic understanding of current role"],
                    "resources": ["Online courses", "Books", "Tutorials", "Practice exercises"]
                },
                {
                    "module_name": "2. Advanced Skills",
                    "description": "Develop advanced technical and professional skills required for the target role.",
                    "duration_weeks": 6,
                    "key_topics": ["Advanced techniques", "Problem solving", "System design", "Best practices"],
                    "prerequisites": ["Completion of Foundations module"],
                    "resources": ["Advanced courses", "Real-world projects", "Mentorship"]
                },
                {
                    "module_name": "3. Practical Experience",
                    "description": "Apply learned skills through hands-on projects and real-world scenarios.",
                    "duration_weeks": 8,
                    "key_topics": ["Project work", "Case studies", "Portfolio building", "Collaboration"],
                    "prerequisites": ["Completion of Advanced Skills"],
                    "resources": ["Project templates", "Team collaboration tools", "Portfolio platforms"]
                },
                {
                    "module_name": "4. Leadership & Soft Skills",
                    "description": "Develop leadership, communication, and interpersonal skills essential for the role.",
                    "duration_weeks": 4,
                    "key_topics": ["Communication", "Team leadership", "Conflict resolution", "Presentation skills"],
                    "prerequisites": ["Professional experience"],
                    "resources": ["Leadership courses", "Communication workshops", "Coaching sessions"]
                },
                {
                    "module_name": "5. Career Transition",
                    "description": "Prepare for the actual transition with resume building, interview prep, and networking.",
                    "duration_weeks": 2,
                    "key_topics": ["Resume optimization", "Interview preparation", "Networking", "Job search strategies"],
                    "prerequisites": ["Completion of all previous modules"],
                    "resources": ["Career coaches", "Resume templates", "Interview guides", "Networking events"]
                }
            ]
        }
    }

    if not api_key:
        print("⚠️ Learning path generation: No API key")
        return fallback_path

    prompt = f"""Create a detailed learning path for someone transitioning from {current_role} to {career_goal}.

Provide 5-7 learning modules with:
- Module name (numbered)
- Description (2-3 sentences explaining what will be learned)
- Duration (in weeks, realistic timeframe)
- Key topics (list of 4-5 specific topics)
- Prerequisites (what's needed before starting this module)
- Resources (specific types of learning resources)

Return as JSON:
{{
  "learning_path": {{
    "title": "Path from {current_role} to {career_goal}",
    "total_duration_weeks": <total weeks>,
    "modules": [
      {{
        "module_name": "1. Module Title",
        "description": "Detailed description of what this module covers",
        "duration_weeks": 4,
        "key_topics": ["Topic 1", "Topic 2", "Topic 3", "Topic 4"],
        "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
        "resources": ["Resource type 1", "Resource type 2", "Resource type 3"]
      }}
    ]
  }}
}}
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        if not response or not hasattr(response, 'text'):
            print("⚠️ Learning path: No response from API")
            return fallback_path

        response_text = response.text.strip()

        if not response_text:
            print("⚠️ Learning path: Empty response")
            return fallback_path

        # Clean and parse JSON response
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        response_text = response_text.strip()
        
        # Extract JSON if wrapped
        start = response_text.find("{")
        end = response_text.rfind("}") + 1
        if start != -1 and end > start:
            response_text = response_text[start:end]

        return json.loads(response_text)

    except json.JSONDecodeError as e:
        print(f"⚠️ Learning path JSON error: {e}")
        return fallback_path
    except Exception as e:
        print(f"⚠️ Learning path error: {e}")
        return fallback_path


def get_roles_and_goals() -> dict:
    """Get available roles and career goals"""
    return {
        "roles": [
            "software-engineer", "data-analyst", "product-manager",
            "designer", "marketing-specialist", "hr-specialist",
            "business-analyst", "project-manager", "devops-engineer"
        ],
        "goals": [
            "senior-software-engineer", "tech-lead", "engineering-manager",
            "data-scientist", "senior-analyst", "product-lead",
            "design-lead", "marketing-manager", "hr-manager",
            "senior-analyst", "program-manager", "devops-architect"
        ]
    }
