"""
Pydantic schemas for resume parsing
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class PersonalInfo(BaseModel):
    name: Optional[str] = "Unknown"
    email: Optional[str] = "Unknown"
    phone: Optional[str] = "Unknown"
    location: Optional[str] = None
    summary: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class CompanyInfo(BaseModel):
    industry: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    other: Optional[Dict[str, Any]] = None


class ExperienceItem(BaseModel):
    company: Optional[str] = None
    company_info: Optional[CompanyInfo] = None
    title: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class Degree(BaseModel):
    level: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    start_year: Optional[str] = None
    end_year: Optional[str] = None
    grade: Optional[str] = None


class ProjectItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: Optional[List[str]] = []
    url: Optional[str] = None


class CertificationItem(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None


class ResumeSchema(BaseModel):
    personal_info: PersonalInfo
    skills: Optional[List[str]] = []
    experience: Optional[List[ExperienceItem]] = []
    education: Optional[List[Degree]] = []
    projects: Optional[List[ProjectItem]] = []
    certifications: Optional[List[CertificationItem]] = []
    languages: Optional[List[str]] = []
    awards: Optional[List[str]] = []
