"""
Verification script for RAG Context Generation
"""
from app_modular import app
from utils.data_fetcher import get_employee_context
from utils.swagger_parser import get_api_capabilities
from models import User

def verify_context_generation():
    with app.app_context():
        # 1. Test Swagger Parser
        print("\n--- Testing Swagger Parser ---")
        capabilities = get_api_capabilities()
        print(f"Capabilities Length: {len(capabilities)}")
        print(f"Sample: {capabilities[:200]}...")
        
        # 2. Test Data Fetcher (Mock User ID 1)
        print("\n--- Testing Data Fetcher (User ID 1) ---")
        user = User.query.get(1)
        if not user:
            print("User ID 1 not found. Skipping data fetcher test.")
        else:
            context = get_employee_context(1)
            print("User Info:", context['user_info'])
            print("Leave Stats:", context['leave_stats'])
            print("Policies Count:", len(context['policies']))
            if context['policies']:
                print("Sample Policy:", context['policies'][0]['title'])

if __name__ == "__main__":
    verify_context_generation()
