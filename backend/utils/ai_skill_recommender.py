"""
Skill Recommendation System using Google Gemini 2.5 Flash
"""
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env", override=True)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def recommend_skills(current_role: str, career_goal: str, department: str = "General") -> list:
    """
    Recommend skills for career development
    
    Args:
        current_role: Current job role
        career_goal: Desired career goal
        department: Department/industry
    
    Returns:
        List of recommended skills
    """
    prompt = f"""You are a career development expert. Recommend skills for someone to develop.

Current Role: {current_role}
Career Goal: {career_goal}
Department: {department}

Provide 8-10 specific skills they should learn to achieve their career goal.
Return as JSON array of objects with: skill, reason, priority (high/medium/low), timeframe

Example format:
[
  {{"skill": "Python", "reason": "Essential for backend development", "priority": "high", "timeframe": "3 months"}},
  ...
]
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Clean and parse JSON response
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        return result.get('skills', [])
    except Exception as e:
        return [
            {"skill": "Leadership", "reason": "Essential for career growth", "priority": "high", "timeframe": "6 months"},
            {"skill": "Communication", "reason": "Important for all roles", "priority": "high", "timeframe": "3 months"}
        ]


def get_trending_skills(department: str = "Technology") -> list:
    """
    Get trending skills for a department
    
    Args:
        department: Department/industry name
    
    Returns:
        List of trending skills
    """
    prompt = f"""List the top 10 trending skills in {department} for 2025.

Return as JSON array with: skill, trend (rising/stable/emerging), demand_level (high/medium/low)

Example:
[
  {{"skill": "AI/ML", "trend": "rising", "demand_level": "high"}},
  ...
]
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Clean and parse JSON response
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        return result.get('skills', [])
    except Exception as e:
        return [
            {"skill": "Artificial Intelligence", "trend": "rising", "demand_level": "high"},
            {"skill": "Cloud Computing", "trend": "stable", "demand_level": "high"}
        ]
