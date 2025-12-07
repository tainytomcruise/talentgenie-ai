"""
Analytics Routes
Endpoints for HR analytics and reporting
"""
from flask import jsonify
from flask_restful import Resource
from models import *
from datetime import datetime, timedelta
import calendar


class AnalyticsSummary(Resource):
    """Overall analytics summary"""
    
    def get(self):
        total_employees = Employee.query.count()
        
        # Calculate avg absenteeism
        today = datetime.utcnow().date()
        start_period = today - timedelta(days=180)
        leaves = LeaveRequest.query.filter(
            LeaveRequest.start_date >= start_period,
            LeaveRequest.status == 'Approved'
        ).all()
        total_days = sum((lv.end_date - lv.start_date).days + 1 for lv in leaves)
        avg_absenteeism = round((total_days / (total_employees * 22 * 6)) * 100, 2) if total_employees else 0
        
        # Training completion
        total_enrollments = EmployeeTraining.query.count()
        completed = EmployeeTraining.query.filter_by(status='Completed').count()
        training_completion = round((completed / total_enrollments) * 100, 2) if total_enrollments else 0
        
        # Retention risk
        employees = Employee.query.all()
        high_risk_count = 0
        for emp in employees:
            emp_leaves = LeaveRequest.query.filter(
                LeaveRequest.emp_id == emp.emp_id,
                LeaveRequest.status == 'Approved',
                LeaveRequest.start_date >= start_period
            ).all()
            leave_days = sum((l.end_date - l.start_date).days + 1 for l in emp_leaves)
            absenteeism_pct = (leave_days / (22 * 6)) * 100
            
            trainings = EmployeeTraining.query.filter_by(emp_id=emp.emp_id).all()
            pending_pct = (len([t for t in trainings if t.status != 'Completed']) / (len(trainings) or 1)) * 100
            
            if absenteeism_pct > 8 or pending_pct > 50:
                high_risk_count += 1
        
        high_retention_risk = round((high_risk_count / total_employees) * 100, 2) if total_employees else 0
        
        return {
            "total_employees": total_employees,
            "avg_absenteeism": avg_absenteeism,
            "training_completion_rate": training_completion,
            "high_retention_risk_percent": high_retention_risk,
            "trends": {
                "employees_vs_last_quarter": 0,
                "absenteeism_vs_last_month": 0,
                "training_vs_last_quarter": 0,
                "retention_vs_last_quarter": 0
            }
        }


class AbsenteeismTrends(Resource):
    """Absenteeism trends over time"""
    
    def get(self):
        today = datetime.utcnow()
        months = []
        approved_data, burnout_data, sickness_data = [], [], []
        
        for i in reversed(range(7)):
            month_start = datetime(today.year, today.month, 1) - timedelta(days=i*30)
            month_end = datetime(month_start.year, month_start.month, 
                               calendar.monthrange(month_start.year, month_start.month)[1])
            months.append(month_start.strftime('%b'))
            
            leaves = LeaveRequest.query.filter(
                LeaveRequest.start_date >= month_start,
                LeaveRequest.start_date <= month_end,
                LeaveRequest.status == 'Approved'
            ).all()
            
            approved_data.append(sum((l.end_date - l.start_date).days + 1 for l in leaves))
            burnout_data.append(sum(1 for l in leaves if l.reason and 'burnout' in l.reason.lower()))
            sickness_data.append(sum(1 for l in leaves if l.reason and 'sick' in l.reason.lower()))
        
        return {
            "categories": months,
            "series": [
                {"name": "Approved Leave", "data": approved_data},
                {"name": "Burnout", "data": burnout_data},
                {"name": "Sickness", "data": sickness_data}
            ]
        }


class RetentionRisk(Resource):
    """Retention risk distribution"""
    
    def get(self):
        employees = Employee.query.all()
        low = medium = high = 0
        start_period = datetime.utcnow().date() - timedelta(days=180)
        
        for emp in employees:
            leaves = LeaveRequest.query.filter(
                LeaveRequest.emp_id == emp.emp_id,
                LeaveRequest.status == 'Approved',
                LeaveRequest.start_date >= start_period
            ).all()
            leave_days = sum((l.end_date - l.start_date).days + 1 for l in leaves)
            absenteeism_pct = (leave_days / (22 * 6)) * 100
            
            trainings = EmployeeTraining.query.filter_by(emp_id=emp.emp_id).all()
            pending_pct = (len([t for t in trainings if t.status != 'Completed']) / (len(trainings) or 1)) * 100
            
            if absenteeism_pct > 8 or pending_pct > 50:
                high += 1
            elif absenteeism_pct > 5 or pending_pct > 30:
                medium += 1
            else:
                low += 1
        
        return {"labels": ["Low Risk", "Medium Risk", "High Risk"], "series": [low, medium, high]}


class TrainingCompletion(Resource):
    """Training completion by department"""
    
    def get(self):
        departments = Department.query.all()
        categories, completed_data, pending_data = [], [], []
        
        for dept in departments:
            emp_ids = [e.emp_id for e in dept.employees]
            if not emp_ids:
                continue
            
            total = EmployeeTraining.query.filter(EmployeeTraining.emp_id.in_(emp_ids)).count()
            completed = EmployeeTraining.query.filter(
                EmployeeTraining.emp_id.in_(emp_ids),
                EmployeeTraining.status == 'Completed'
            ).count()
            
            categories.append(dept.name)
            completed_data.append(round((completed / total) * 100 if total else 0, 2))
            pending_data.append(round(((total - completed) / total) * 100 if total else 0, 2))
        
        return {
            "categories": categories,
            "series": [
                {"name": "Completed", "data": completed_data},
                {"name": "Pending", "data": pending_data}
            ]
        }


class DepartmentAnalytics(Resource):
    """Department-wise analytics"""
    
    def get(self):
        departments = Department.query.all()
        department_data = []
        
        for dept in departments:
            emp_count = dept.employees.count()
            emp_ids = [e.emp_id for e in dept.employees]
            
            if emp_ids:
                total_leaves = LeaveRequest.query.filter(
                    LeaveRequest.emp_id.in_(emp_ids),
                    LeaveRequest.status == 'Approved'
                ).all()
                leave_days = sum((l.end_date - l.start_date).days + 1 for l in total_leaves)
                absenteeism = round((leave_days / (emp_count * 22 * 6)) * 100 if emp_count else 0, 2)
                
                total_training = EmployeeTraining.query.filter(EmployeeTraining.emp_id.in_(emp_ids)).count()
                completed_training = EmployeeTraining.query.filter(
                    EmployeeTraining.emp_id.in_(emp_ids),
                    EmployeeTraining.status == 'Completed'
                ).count()
                pending_training = total_training - completed_training
            else:
                absenteeism = pending_training = total_training = 0
            
            risk_level = "Low Risk"
            if absenteeism > 5:
                risk_level = "Medium Risk"
            if absenteeism > 8:
                risk_level = "High Risk"
            
            insights = []
            if pending_training > 0:
                insights.append(f"{int((pending_training / (total_training or 1)) * 100)}% haven't completed training")
            insights.append(f"Avg absenteeism: {absenteeism}%")
            
            department_data.append({
                "department": dept.name,
                "risk_level": risk_level,
                "employee_count": emp_count,
                "pending_training": pending_training,
                "absenteeism": absenteeism,
                "insights": insights
            })
        
        return department_data


class AnalyticsOverview(Resource):
    """Comprehensive analytics overview"""
    
    def get(self):
        total_employees = Employee.query.count()
        total_jobs = Job.query.count()
        open_jobs = Job.query.filter_by(status='Open').count()
        total_applicants = Applicant.query.count()
        
        # Training stats
        total_trainings = Training.query.count()
        total_enrollments = EmployeeTraining.query.count()
        completed_trainings = EmployeeTraining.query.filter_by(status='Completed').count()
        training_completion_rate = round((completed_trainings / total_enrollments) * 100, 2) if total_enrollments else 0
        
        # Leave stats
        total_leaves = LeaveRequest.query.count()
        pending_leaves = LeaveRequest.query.filter_by(status='Pending').count()
        approved_leaves = LeaveRequest.query.filter_by(status='Approved').count()
        
        # Department breakdown
        departments = Department.query.all()
        dept_breakdown = []
        for dept in departments:
            dept_breakdown.append({
                "name": dept.name,
                "employee_count": dept.employees.count(),
                "open_positions": Job.query.filter_by(dept_id=dept.dept_id, status='Open').count()
            })
        
        return {
            "overview": {
                "total_employees": total_employees,
                "total_jobs": total_jobs,
                "open_jobs": open_jobs,
                "total_applicants": total_applicants
            },
            "training": {
                "total_programs": total_trainings,
                "total_enrollments": total_enrollments,
                "completed": completed_trainings,
                "completion_rate": training_completion_rate
            },
            "leave": {
                "total_requests": total_leaves,
                "pending": pending_leaves,
                "approved": approved_leaves
            },
            "departments": dept_breakdown
        }


class RecruitmentAnalytics(Resource):
    """Recruitment funnel analytics"""
    
    def get(self):
        jobs = Job.query.all()
        
        funnel_data = []
        for job in jobs:
            applicants = Applicant.query.filter_by(job_id=job.job_id).all()
            
            status_counts = {
                "Applied": 0,
                "Screening": 0,
                "Interview": 0,
                "Offered": 0,
                "Hired": 0,
                "Rejected": 0
            }
            
            for applicant in applicants:
                if applicant.status in status_counts:
                    status_counts[applicant.status] += 1
            
            funnel_data.append({
                "job_title": job.title,
                "job_id": job.job_id,
                "total_applicants": len(applicants),
                "funnel": status_counts,
                "conversion_rate": round((status_counts["Hired"] / len(applicants)) * 100, 2) if applicants else 0
            })
        
        return {
            "recruitment_funnel": funnel_data,
            "total_jobs": len(jobs),
            "total_applicants": Applicant.query.count()
        }


class TrainingAnalytics(Resource):
    """Training program analytics"""
    
    def get(self):
        trainings = Training.query.all()
        
        training_stats = []
        for training in trainings:
            enrollments = EmployeeTraining.query.filter_by(training_id=training.training_id).all()
            completed = [e for e in enrollments if e.status == 'Completed']
            
            avg_score = sum([e.score for e in completed if e.score]) / len(completed) if completed else 0
            
            training_stats.append({
                "training_id": training.training_id,
                "title": training.title,
                "category": training.category,
                "total_enrolled": len(enrollments),
                "completed": len(completed),
                "completion_rate": round((len(completed) / len(enrollments)) * 100, 2) if enrollments else 0,
                "average_score": round(avg_score, 2)
            })
        
        return {
            "training_programs": training_stats,
            "total_programs": len(trainings),
            "total_enrollments": EmployeeTraining.query.count()
        }
