/**
 * API Configuration
 *
 * In development: Vite proxy forwards /api requests to http://localhost:5001
 * In production: Update API_BASE_URL to your production backend URL
 */

// Use empty string in development to leverage Vite proxy
// In production, set this to your backend URL (e.g., 'https://api.yourcompany.com')
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Backend server info (for reference)
export const BACKEND_URL = 'http://localhost:5001'
export const BACKEND_PORT = 5001

// API endpoints (for documentation/reference)
export const API_ENDPOINTS = {
  // Authentication
  AUTH_LOGIN: '/api/auth/login',
  AUTH_REGISTER: '/api/auth/register',
  AUTH_ME: '/api/auth/me',

  // Recruitment
  RECRUITMENT_UPLOAD: '/api/recruitment/upload',
  RECRUITMENT_PARSE: '/api/recruitment/parse',
  RECRUITMENT_MATCH: '/api/recruitment/match',
  RECRUITMENT_QUESTIONS: '/api/recruitment/questions',

  // Analytics
  ANALYTICS_SUMMARY: '/api/analytics/summary',
  ANALYTICS_ABSENTEEISM: '/api/analytics/absenteeism-trends',
  ANALYTICS_RETENTION: '/api/analytics/retention-risk',
  ANALYTICS_TRAINING: '/api/analytics/training-completion',
  ANALYTICS_DEPARTMENTS: '/api/analytics/departments',
  ANALYTICS_OVERVIEW: '/api/analytics/overview',

  // Policy & Job Generation
  POLICY_GENERATE_JOB: '/api/policy/generate/job',
  POLICY_GENERATE_DOCUMENT: '/api/policy/generate/document',
  POLICY_LOCATIONS: '/api/policy/locations',
  POLICY_TONES: '/api/policy/tones',

  // HR Chatbot
  CHAT_SEND: '/api/askhr/chat',
  CHAT_HISTORY: '/api/chat/history',

  // Learning & Development
  LEARNING_GENERATE: '/api/learning/path/generate',
  LEARNING_PROGRESS: '/api/learning/progress',
  LEARNING_COMPLETE: '/api/learning/module/complete',
  LEARNING_ROLES_GOALS: '/api/learning/roles-goals',

  // Sentiment Analysis
  SENTIMENT_ANALYZE: '/api/sentiment/analyze',
  SENTIMENT_TREND: '/api/sentiment/trend',
  SENTIMENT_THEMES: '/api/sentiment/themes',

  // Wellness
  WELLNESS_RESOURCES: '/api/wellness/resources',
  WELLNESS_TIPS: '/api/wellness/tips',
  WELLNESS_EVENTS: '/api/wellness/events',
  WELLNESS_REGISTER: '/api/wellness/events/register',

  // HR Wellness
  HR_WELLNESS_RESOURCES: '/api/hr/wellness/resources',
  HR_WELLNESS_ALERTS: '/api/hr/wellness/alerts',
  HR_WELLNESS_MILESTONES: '/api/hr/wellness/milestones',
  HR_WELLNESS_AWARDS: '/api/hr/wellness/awards',
  HR_WELLNESS_BIRTHDAYS: '/api/hr/wellness/birthdays',
  HR_WELLNESS_SURVEYS: '/api/hr/wellness/surveys',

  // Employee Dashboard
  EMPLOYEE_DASHBOARD: '/api/employee/dashboard/summary',
  EMPLOYEE_SKILLS: '/api/employee/ai_skill_recommendations',
  EMPLOYEE_REFERENCE: '/api/employee/document_request/reference',
  EMPLOYEE_EMPLOYMENT_PROOF: '/api/employee/document_request/employment_proof',

  // Skills
  SKILLS_TRENDING: '/api/skills/trending',
}

export default {
  API_BASE_URL,
  BACKEND_URL,
  BACKEND_PORT,
  API_ENDPOINTS,
}

