"""
Swagger Parser Utility
Parses swagger.yaml to extract API capabilities for the AI Chatbot context.
"""
import yaml
import os

def get_api_capabilities(swagger_path="swagger.yaml"):
    """
    Parses the swagger.yaml file and returns a summary of available API endpoints.
    
    Returns:
        str: A formatted string listing endpoints and their descriptions.
    """
    try:
        # Resolve absolute path if needed, assuming it's in the backend root or passed correctly
        if not os.path.isabs(swagger_path):
            # Try to find it relative to this file's parent (backend/utils -> backend/)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            swagger_path = os.path.join(base_dir, swagger_path)
            
        if not os.path.exists(swagger_path):
            return "API capabilities documentation not found."

        with open(swagger_path, 'r') as f:
            spec = yaml.safe_load(f)
            
        summary = "Available System Capabilities (API Endpoints):\n"
        
        paths = spec.get('paths', {})
        for path, methods in paths.items():
            for method, details in methods.items():
                # Skip if it's not a standard HTTP method
                if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                    continue
                    
                description = details.get('summary', details.get('description', 'No description'))
                # Truncate long descriptions
                if len(description) > 100:
                    description = description[:97] + "..."
                    
                summary += f"- {method.upper()} {path}: {description}\n"
                
        return summary
        
    except Exception as e:
        print(f"Error parsing swagger.yaml: {e}")
        return "Error loading system capabilities."
