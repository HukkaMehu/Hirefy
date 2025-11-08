"""
Green Scenario - Sarah Chen
Clean candidate with verified employment, strong GitHub presence, positive references
Expected Risk Score: GREEN
"""

# Candidate Profile
CANDIDATE_DATA = {
    "name": "Sarah Chen",
    "email": "sarah.chen@email.com",
    "phone": "+1-555-0101",
    "github_username": "sarahchen",
    "linkedin": "linkedin.com/in/sarahchen"
}

# CV Data (what the candidate claims)
CV_DATA = {
    "employment_history": [
        {
            "company": "TechCorp Inc",
            "title": "Senior Software Engineer",
            "start_date": "2021-03-01",
            "end_date": "2024-10-31",
            "responsibilities": [
                "Led development of microservices architecture",
                "Mentored junior developers",
                "Implemented CI/CD pipelines"
            ],
            "technologies": ["Python", "React", "AWS", "Docker", "Kubernetes"]
        },
        {
            "company": "StartupXYZ",
            "title": "Software Engineer",
            "start_date": "2019-06-01",
            "end_date": "2021-02-28",
            "responsibilities": [
                "Built RESTful APIs",
                "Developed frontend features",
                "Participated in code reviews"
            ],
            "technologies": ["Python", "JavaScript", "PostgreSQL", "Redis"]
        },
        {
            "company": "InnovateLabs",
            "title": "Junior Developer",
            "start_date": "2017-09-01",
            "end_date": "2019-05-31",
            "responsibilities": [
                "Fixed bugs and implemented features",
                "Wrote unit tests",
                "Collaborated with design team"
            ],
            "technologies": ["Python", "Django", "MySQL"]
        }
    ],
    "education": [
        {
            "institution": "University of California, Berkeley",
            "degree": "Bachelor of Science",
            "major": "Computer Science",
            "graduation_date": "2017-05-15",
            "gpa": "3.8"
        }
    ],
    "skills": ["Python", "React", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Redis", "Django"],
    "certifications": ["AWS Certified Solutions Architect"]
}

# Supporting Documents (paystubs match CV perfectly)
PAYSTUB_DATA = [
    {
        "company": "TechCorp Inc",
        "employee_name": "Sarah Chen",
        "title": "Senior Software Engineer",
        "pay_period": "2024-10-01 to 2024-10-15",
        "gross_pay": "$8,500.00"
    },
    {
        "company": "StartupXYZ",
        "employee_name": "Sarah Chen",
        "title": "Software Engineer",
        "pay_period": "2021-02-01 to 2021-02-15",
        "gross_pay": "$5,200.00"
    }
]

# Diploma Data (matches CV)
DIPLOMA_DATA = {
    "institution": "University of California, Berkeley",
    "degree": "Bachelor of Science",
    "major": "Computer Science",
    "graduation_date": "May 15, 2017",
    "honors": "Cum Laude"
}

# HR Verification Results (all verified)
HR_VERIFICATION_RESULTS = [
    {
        "company": "TechCorp Inc",
        "verified": True,
        "title_confirmed": "Senior Software Engineer",
        "dates_confirmed": "March 2021 - October 2024",
        "eligible_for_rehire": True,
        "hr_contact": "Jane Smith, HR Manager"
    },
    {
        "company": "StartupXYZ",
        "verified": True,
        "title_confirmed": "Software Engineer",
        "dates_confirmed": "June 2019 - February 2021",
        "eligible_for_rehire": True,
        "hr_contact": "Bob Johnson, HR Director"
    },
    {
        "company": "InnovateLabs",
        "verified": True,
        "title_confirmed": "Junior Developer",
        "dates_confirmed": "September 2017 - May 2019",
        "eligible_for_rehire": True,
        "hr_contact": "Alice Williams, HR Coordinator"
    }
]

# Reference Check Results (all positive)
REFERENCE_RESULTS = [
    {
        "name": "Tom Anderson",
        "relationship": "Direct Manager at TechCorp Inc",
        "overlap_verified": True,
        "feedback": {
            "performance": "Excellent - consistently exceeded expectations",
            "technical_skills": "Very strong in Python and cloud architecture",
            "collaboration": "Great team player, excellent mentor",
            "strengths": "Problem-solving, leadership, technical depth",
            "areas_for_improvement": "Could delegate more, tends to take on too much",
            "would_rehire": True
        },
        "quotes": [
            "Sarah was one of our top performers",
            "She led the migration to microservices which was a huge success",
            "I'd hire her again in a heartbeat"
        ]
    },
    {
        "name": "Lisa Martinez",
        "relationship": "Tech Lead at StartupXYZ",
        "overlap_verified": True,
        "feedback": {
            "performance": "Strong - delivered quality work consistently",
            "technical_skills": "Solid full-stack developer",
            "collaboration": "Easy to work with, good communicator",
            "strengths": "Quick learner, reliable, good code quality",
            "areas_for_improvement": "Could be more proactive in suggesting improvements",
            "would_rehire": True
        },
        "quotes": [
            "Sarah was a reliable team member",
            "Her code was always well-tested and documented",
            "She grew a lot during her time here"
        ]
    }
]

# GitHub Analysis Results (strong activity matching claims)
GITHUB_ANALYSIS = {
    "username": "sarahchen",
    "profile_found": True,
    "total_repos": 45,
    "owned_repos": 12,
    "contributed_repos": 33,
    "total_commits": 2847,
    "commit_timeline": {
        "2017": 245,
        "2018": 412,
        "2019": 398,
        "2020": 456,
        "2021": 523,
        "2022": 387,
        "2023": 289,
        "2024": 137
    },
    "languages": {
        "Python": 45.2,
        "JavaScript": 28.7,
        "TypeScript": 12.3,
        "Go": 8.1,
        "Shell": 3.2,
        "Other": 2.5
    },
    "activity_during_employment": {
        "TechCorp Inc (2021-2024)": "High activity - 1336 commits",
        "StartupXYZ (2019-2021)": "Moderate activity - 854 commits",
        "InnovateLabs (2017-2019)": "Moderate activity - 657 commits"
    },
    "notable_projects": [
        {
            "name": "microservices-platform",
            "description": "Scalable microservices architecture with Docker and Kubernetes",
            "stars": 234,
            "language": "Python",
            "last_updated": "2024-10-15"
        },
        {
            "name": "api-gateway",
            "description": "High-performance API gateway with rate limiting",
            "stars": 89,
            "language": "Go",
            "last_updated": "2024-09-20"
        }
    ],
    "code_quality_score": 8,
    "skills_match": 92.5
}

# Expected Fraud Flags (none)
EXPECTED_FRAUD_FLAGS = []

# Expected Risk Score
EXPECTED_RISK_SCORE = "GREEN"

# Expected Report Summary
EXPECTED_REPORT_SUMMARY = """
Sarah Chen is a highly qualified Senior Software Engineer with a clean verification record. 
All employment dates and titles have been verified with HR departments. References from 
former managers provide consistently positive feedback, highlighting her technical skills, 
leadership abilities, and reliability. Her GitHub profile shows strong, consistent activity 
that aligns perfectly with her claimed employment timeline and technical skills. No red 
flags or concerns were identified during the verification process.
"""

# Conversational Flow (no conflicts to resolve)
CONVERSATIONAL_FLOW = [
    {
        "agent": "Hi Sarah! I'm here to help collect your documents for verification. Let's start with your CV. Could you please upload it?",
        "candidate": "[uploads CV]",
        "agent_action": "extract_cv"
    },
    {
        "agent": "Great! I can see you worked at TechCorp Inc from March 2021 to October 2024. Could you please upload a recent pay stub from TechCorp Inc?",
        "candidate": "[uploads paystub]",
        "agent_action": "extract_paystub"
    },
    {
        "agent": "Perfect! Now, could you upload a pay stub from StartupXYZ to verify your employment there?",
        "candidate": "[uploads paystub]",
        "agent_action": "extract_paystub"
    },
    {
        "agent": "Excellent! I see you have a degree from UC Berkeley. Could you please upload your diploma?",
        "candidate": "[uploads diploma]",
        "agent_action": "extract_diploma"
    },
    {
        "agent": "Thank you! Everything looks consistent. Here's a summary of what I've collected:\n\n- Employment at TechCorp Inc (2021-2024) - Verified with paystub\n- Employment at StartupXYZ (2019-2021) - Verified with paystub\n- Employment at InnovateLabs (2017-2019)\n- BS in Computer Science from UC Berkeley (2017) - Verified with diploma\n\nDoes everything look correct?",
        "candidate": "Yes, that's all correct!",
        "agent_action": "finalize_collection"
    }
]
