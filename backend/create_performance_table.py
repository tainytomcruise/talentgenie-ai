from app_modular import app
from models import db, EmployeePerformance

with app.app_context():
    # Create the table
    # Since db.create_all() only creates tables that don't exist, 
    # and we just added EmployeePerformance to models, this should work.
    # However, to be safe and specific, we can try to create just this table 
    # or rely on create_all if we trust it won't touch others.
    # SQLAlchemy's create_all is safe.
    print("Creating employee_performance table...")
    db.create_all()
    print("Done.")
