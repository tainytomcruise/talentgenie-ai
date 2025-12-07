"""
Wellness Tips Generator using Google Gemini 2.5 Flash
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


def generate_wellness_tips(category: str = "general") -> list:
    """
    Generate a single wellness tip
    
    Args:
        category: Category of tips (general, mental, physical, nutrition, sleep)

    Returns:
        A single wellness tip based on one or more of the categories
    """

    # Category-specific fallback tips
    fallback_tips = {
        "general": [
            {"tip": "Take regular breaks every hour to stretch and move around", "category": "general", "difficulty": "easy"},
            {"tip": "Stay hydrated by drinking at least 8 glasses of water daily", "category": "general", "difficulty": "easy"},
            {"tip": "Maintain a consistent sleep schedule, even on weekends", "category": "general", "difficulty": "medium"},
            {"tip": "Practice the 20-20-20 rule: Every 20 minutes, look at something 20 feet away for 20 seconds", "category": "general", "difficulty": "easy"},
            {"tip": "Keep healthy snacks at your desk to avoid unhealthy vending machine choices", "category": "general", "difficulty": "easy"}
        ],
        "mental": [
            {"tip": "Practice mindfulness meditation for 10 minutes daily to reduce stress", "category": "mental", "difficulty": "medium"},
            {"tip": "Use the 4-7-8 breathing technique when feeling anxious: Breathe in for 4, hold for 7, exhale for 8", "category": "mental", "difficulty": "easy"},
            {"tip": "Set clear boundaries between work and personal time to prevent burnout", "category": "mental", "difficulty": "medium"},
            {"tip": "Keep a gratitude journal and write down 3 things you're thankful for each day", "category": "mental", "difficulty": "easy"},
            {"tip": "Take 'mental health days' when needed - your wellbeing is a priority", "category": "mental", "difficulty": "medium"}
        ],
        "physical": [
            {"tip": "Stand up and stretch every 30 minutes to improve circulation and reduce muscle tension", "category": "physical", "difficulty": "easy"},
            {"tip": "Exercise for at least 30 minutes, 5 days a week - even a brisk walk counts", "category": "physical", "difficulty": "medium"},
            {"tip": "Adjust your workspace ergonomics: Monitor at eye level, feet flat on floor", "category": "physical", "difficulty": "easy"},
            {"tip": "Take the stairs instead of the elevator whenever possible", "category": "physical", "difficulty": "easy"},
            {"tip": "Practice desk exercises: shoulder rolls, neck stretches, and wrist rotations", "category": "physical", "difficulty": "easy"}
        ],
        "nutrition": [
            {"tip": "Eat a balanced breakfast with protein, whole grains, and fruits within an hour of waking", "category": "nutrition", "difficulty": "medium"},
            {"tip": "Pack healthy lunches to avoid relying on fast food or vending machines", "category": "nutrition", "difficulty": "medium"},
            {"tip": "Limit caffeine intake to before 2 PM to avoid sleep disruption", "category": "nutrition", "difficulty": "easy"},
            {"tip": "Include colorful vegetables in every meal - aim for 5 different colors daily", "category": "nutrition", "difficulty": "medium"},
            {"tip": "Keep healthy snacks visible: nuts, fruits, yogurt instead of chips and candy", "category": "nutrition", "difficulty": "easy"}
        ],
        "sleep": [
            {"tip": "Maintain a consistent sleep schedule: Go to bed and wake up at the same time daily", "category": "sleep", "difficulty": "medium"},
            {"tip": "Create a bedtime routine: Dim lights, no screens 30 minutes before bed", "category": "sleep", "difficulty": "medium"},
            {"tip": "Keep your bedroom cool (60-67°F) and dark for optimal sleep quality", "category": "sleep", "difficulty": "easy"},
            {"tip": "Avoid heavy meals, alcohol, and exercise at least 3 hours before bedtime", "category": "sleep", "difficulty": "medium"},
            {"tip": "If you can't fall asleep after 20 minutes, get up and do a calming activity", "category": "sleep", "difficulty": "easy"}
        ]
    }

    # Return fallback if no API key or invalid category
    if not api_key or category not in fallback_tips:
        return fallback_tips.get(category, fallback_tips["general"])

    prompt = f"""Generate a specific, actionable wellness tip for the category: {category}

Requirements:
- Each tip should be practical and easy to implement
- Include difficulty level (easy/medium/hard)
- Focus on workplace wellness
- Make tips diverse and actionable

Return as JSON array:
[
  {{"tip": "specific actionable tip", "category": "{category}", "difficulty": "easy"}},
  ...
]
"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        if not response or not hasattr(response, 'text'):
            print(f"⚠️ Wellness tips: No response for {category}")
            return fallback_tips.get(category, fallback_tips["general"])

        response_text = response.text.strip()

        if not response_text:
            print(f"⚠️ Wellness tips: Empty response for {category}")
            return fallback_tips.get(category, fallback_tips["general"])

        # Clean JSON
        if response_text.startswith('```json'):
            response_text = response_text[7:-3]
        elif response_text.startswith('```'):
            response_text = response_text[3:-3]
        response_text = response_text.strip()
        
        # Extract JSON array
        start = response_text.find("[")
        end = response_text.rfind("]") + 1
        if start != -1 and end > start:
            response_text = response_text[start:end]

        tips = json.loads(response_text)

        # Validate response is a list
        if not isinstance(tips, list) or len(tips) == 0:
            return fallback_tips.get(category, fallback_tips["general"])

        return tips

    except json.JSONDecodeError as e:
        print(f"⚠️ Wellness tips JSON error for {category}: {e}")
        return fallback_tips.get(category, fallback_tips["general"])
    except Exception as e:
        print(f"⚠️ Wellness tips error for {category}: {e}")
        return fallback_tips.get(category, fallback_tips["general"])
