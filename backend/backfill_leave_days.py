from app_modular import app
from models import db, LeaveRequest

def backfill_leave_days():
    with app.app_context():
        # Find all requests to ensure correct calculation
        requests = LeaveRequest.query.all()
        
        print(f"Found {len(requests)} total leave requests. Recalculating days...")
        
        count = 0
        for req in requests:
            if req.start_date and req.end_date:
                # Calculate days
                if req.start_date == req.end_date:
                    days = 0.5
                else:
                    days = (req.end_date - req.start_date).days + 1
                
                req.number_of_days = float(days)
                count += 1
                print(f"Updated Leave ID {req.leave_id}: {req.start_date} to {req.end_date} = {days} days")
            else:
                print(f"Skipping Leave ID {req.leave_id}: Missing dates")
        
        try:
            db.session.commit()
            print(f"Successfully updated {count} records.")
        except Exception as e:
            db.session.rollback()
            print(f"Error committing changes: {e}")

if __name__ == "__main__":
    backfill_leave_days()
