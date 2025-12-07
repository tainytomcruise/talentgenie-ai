"""
Data Fetcher Utility
Fetches dynamic data (User Profile, Leave Stats) and static data (Policies) for the AI Chatbot context.
"""
from models import User, Employee, Policy, LeaveRequest, db
from sqlalchemy import func

def get_employee_context(user_id):
    """
    Fetches relevant context for a specific employee.
    
    Args:
        user_id (int): The ID of the user.
        
    Returns:
        dict: A dictionary containing user_info, leave_stats, and policies.
    """
    context = {
        "user_info": {},
        "leave_stats": {},
        "policies": []
    }
    
    try:
        # 1. Fetch User and Employee details
        user = User.query.get(user_id)
        if user:
            context["user_info"] = {
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "joined_at": user.created_at.strftime('%Y-%m-%d') if user.created_at else "Unknown"
            }
            
            if user.employee:
                emp = user.employee
                context["user_info"].update({
                    "job_title": emp.job_title,
                    "department": emp.department.name if emp.department else "Unassigned",
                    "manager": emp.manager.user.name if emp.manager and emp.manager.user else "None"
                })
                
                # 2. Calculate Leave Stats
                # Total leaves taken (Approved only)
                approved_leaves = [req.number_of_days or 0 for req in emp.leave_requests if req.status == 'Approved']
                total_taken = sum(approved_leaves)
                
                # Pending requests
                pending_count = LeaveRequest.query.filter_by(emp_id=emp.emp_id, status='Pending').count()
                
                context["leave_stats"] = {
                    "leaves_taken": total_taken,
                    "pending_requests": pending_count,
                    # Assuming a standard policy of 20 days for now, or fetch from policy if structured
                    "standard_allowance": 20, 
                    "remaining_leaves": 20 - total_taken
                }

        # 3. Fetch All Policies
        # In a larger system, we might use vector search here. For now, fetch all active policies.
        policies = Policy.query.all()
        for p in policies:
            context["policies"].append({
                "title": p.title,
                "category": p.category,
                "content": p.content
            })
            
    except Exception as e:
        print(f"Error fetching employee context: {e}")
        
    return context
