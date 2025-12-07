import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from utils.swagger_parser import get_api_capabilities
from utils.data_fetcher import get_employee_context

load_dotenv(Path(__file__).parent.parent / ".env", override=True)

# Setup Gemini with validation
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)


def get_hr_response(question: str, user_id: int = None) -> str:
    """
    Answer HR policy questions using Google Gemini 2.5 Flash with RAG and DB Context.
    
    Args:
        question: Employee's question
        user_id: ID of the user asking the question (optional, for context)
    
    Returns:
        AI-generated answer
    """
    # Check API key
    if not api_key:
        return "I apologize, but I'm currently unable to process requests. Please contact HR directly for assistance."

    # 1. Fetch Context
    context_data = get_employee_context(user_id) if user_id else {"user_info": {}, "leave_stats": {}, "policies": []}
    api_capabilities = get_api_capabilities()
    
    # 2. Construct System Prompt
    user_info = context_data.get("user_info", {})
    leave_stats = context_data.get("leave_stats", {})
    policies = context_data.get("policies", [])
    
    user_context_str = "User Profile:\n"
    if user_info:
        user_context_str += f"- Name: {user_info.get('name')}\n"
        user_context_str += f"- Role: {user_info.get('role')}\n"
        user_context_str += f"- Department: {user_info.get('department')}\n"
    else:
        user_context_str += "- Guest User (No profile found)\n"
        
    leave_context_str = "Leave Balance & Stats:\n"
    if leave_stats:
        leave_context_str += f"- Leaves Taken: {leave_stats.get('leaves_taken')} days\n"
        leave_context_str += f"- Remaining Balance: {leave_stats.get('remaining_leaves')} days (out of {leave_stats.get('standard_allowance')})\n"
        leave_context_str += f"- Pending Requests: {leave_stats.get('pending_requests')}\n"
    
    policy_context_str = "Company HR Policies:\n"
    for policy in policies:
        policy_context_str += f"\n--- POLICY: {policy.get('title')} ---\n{policy.get('content')}\n"
        
    system_prompt = f"""You are an intelligent and helpful HR Assistant for our company.
Your goal is to answer employee questions accurately using ONLY the provided context.

=== CONTEXT START ===

{user_context_str}

{leave_context_str}

{policy_context_str}

{api_capabilities}

=== CONTEXT END ===

**STRICT RULES:**
1.  **Scope Enforcement**: Answer ONLY based on the context provided above (User Profile, Leave Stats, Policies, and System Capabilities).
2.  **Out of Scope**: If the user asks about something not in the context (e.g., general world knowledge, celebrity news, code generation unrelated to this system), politely refuse: "I can only answer questions related to company policies, your profile, and HR data."
3.  **Data Privacy**: You have access to the specific user's data shown above. Do NOT hallucinate data for other users.
4.  **System Capabilities**: If the user asks how to do something (e.g., "How do I apply for leave?"), refer to the "System Capabilities" list to confirm if the feature exists and guide them (e.g., "You can submit a leave request via the Leave Management section.").
5.  **Tone**: Professional, empathetic, and concise.

Employee Question: {question}

Answer:"""

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(system_prompt)

        if not response or not hasattr(response, 'text'):
            print("⚠️ HR Chatbot: No response from API")
            return "I apologize, but I'm having trouble processing your request. Please try again or contact HR directly."

        response_text = response.text.strip()

        if not response_text:
            print("⚠️ HR Chatbot: Empty response")
            return "I apologize, but I couldn't generate a response. Please rephrase your question or contact HR directly."

        return response_text

    except Exception as e:
        print(f"⚠️ HR Chatbot error: {e}")
        return "I apologize, but I'm having trouble processing your request. Please try again later or contact HR directly for assistance."
