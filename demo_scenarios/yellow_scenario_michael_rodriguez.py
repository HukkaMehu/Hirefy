"""
Yellow Scenario - Michael Rodriguez
Mid-level developer with employment gap, moderate GitHub activity, mixed references
Expected Risk Score: YELLOW
"""

# Candidate Profile
CANDIDATE_DATA = {
    "name": "Michael Rodriguez",
    "email": "michael.rodriguez@email.com",
    "phone": "+1-555-0202",
    "github_username": "mrodriguez",
    "linkedin": "linkedin.com/in/michaelrodriguez"
}

# CV Data (with a gap)
CV_DATA = {
    "employment_history": [
        {
            "company": "DataSystems Corp",
            "title": "Senior Developer",
            "start_date": "2023-01-15",
            "end_date": "2024-11-01",
            "responsibilities": [
                "Developed data processing pipelines",
                "Led team of 3 developers",
                "Optimized database queries"
            ],
            "technologies": ["Python", "PostgreSQL", "Apache Spark", "AWS"]
        },
        {
            "company": "CloudTech Solutions",
            "title": "Software Developer",
            "start_date": "2019-03-01",
            "end_date": "2021-08-31",
            "responsibilities": [
                "Built cloud-native applications",
                "Implemented REST APIs",
                "Maintained legacy systems"
            ],
            "technologies": ["Java", "Spring Boot", "AWS", "Docker"]
        },
        {
            "company": "WebDev Inc",
            "title": "Junior Developer",
            "start_date": "2017-06-01",
            "end_date": "2019-02-28",
            "responsibilities": [
                "Developed web applications",
                "Fixed bugs",
                "Wrote documentation"
            ],
            "technologies": ["JavaScript", "Node.js", "MongoDB"]
        }
    ],
    "education": [
        {
            "institution": "State University",
            "degree": "Bachelor of Science",
            "major": "Computer Science",
            "graduation_date": "2017-05-20",
            "gpa": "3.4"
        }
    ],
    "skills": ["Python", "Java", "PostgreSQL", "AWS", "Docker", "Apache Spark"],
    "certifications": []
}

# Supporting Documents (some missing)
PAYSTUB_DATA = [
    {
        "company": "DataSystems Corp",
        "employee_name": "Michael Rodriguez",
        "title": "Senior Developer",
        "pay_period": "2024-10-01 to 2024-10-15",
        "gross_pay": "$6,800.00"
    }
    # Missing paystubs for CloudTech and WebDev
]

# Diploma Data (matches CV)
DIPLOMA_DATA = {
    "institution": "State University",
    "degree": "Bachelor of Science",
    "major": "Computer Science",
    "graduation_date": "May 20, 2017",
    "honors": None
}

# HR Verification Results (mixed)
HR_VERIFICATION_RESULTS = [
    {
        "company": "DataSystems Corp",
        "verified": True,
        "title_confirmed": "Senior Developer",
        "dates_confirmed": "January 2023 - November 2024",
        "eligible_for_rehire": True,
        "hr_contact": "Karen White, HR Manager"
    },
    {
        "company": "CloudTech Solutions",
        "verified": True,
        "title_confirmed": "Software Developer",
        "dates_confirmed": "March 2019 - August 2021",
        "eligible_for_rehire": "Neutral - no comment",
        "hr_contact": "David Lee, HR Director"
    },
    {
        "company": "WebDev Inc",
        "verified": False,
        "reason": "Company no longer in business",
        "hr_contact": None
    }
]

# Reference Check Results (mixed feedback)
REFERENCE_RESULTS = [
    {
        "name": "Jennifer Park",
        "relationship": "Manager at DataSystems Corp",
        "overlap_verified": True,
        "feedback": {
            "performance": "Good - met expectations most of the time",
            "technical_skills": "Solid Python skills, learning Spark",
            "collaboration": "Generally good, occasional communication issues",
            "strengths": "Technical problem-solving, independent worker",
            "areas_for_improvement": "Could be more proactive in team meetings, sometimes misses deadlines",
            "would_rehire": "Maybe - depends on the role"
        },
        "quotes": [
            "Michael is technically capable",
            "He sometimes struggled with time management",
            "He works best independently rather than in collaborative settings"
        ]
    },
    {
        "name": "Robert Chen",
        "relationship": "Colleague at CloudTech Solutions",
        "overlap_verified": True,
        "feedback": {
            "performance": "Average - completed assigned tasks",
            "technical_skills": "Decent Java developer",
            "collaboration": "Okay, but kept to himself",
            "strengths": "Reliable for routine tasks",
            "areas_for_improvement": "Needs to take more initiative, improve communication",
            "would_rehire": "Uncertain"
        },
        "quotes": [
            "Michael was a quiet team member",
            "He did his work but didn't go above and beyond",
            "I didn't work closely with him"
        ]
    }
]

# GitHub Analysis Results (moderate activity with gap)
GITHUB_ANALYSIS = {
    "username": "mrodriguez",
    "profile_found": True,
    "total_repos": 18,
    "owned_repos": 6,
    "contributed_repos": 12,
    "total_commits": 847,
    "commit_timeline": {
        "2017": 89,
        "2018": 134,
        "2019": 156,
        "2020": 98,
        "2021": 67,
        "2022": 12,  # Gap year - very low activity
        "2023": 178,
        "2024": 113
    },
    "languages": {
        "Python": 38.5,
        "Java": 32.1,
        "JavaScript": 18.7,
        "Shell": 6.2,
        "Other": 4.5
    },
    "activity_during_employment": {
        "DataSystems Corp (2023-2024)": "Moderate activity - 291 commits",
        "CloudTech Solutions (2019-2021)": "Low activity - 321 commits",
        "WebDev Inc (2017-2019)": "Moderate activity - 223 commits"
    },
    "notable_projects": [
        {
            "name": "data-pipeline",
            "description": "ETL pipeline for data processing",
            "stars": 12,
            "language": "Python",
            "last_updated": "2024-10-05"
        },
        {
            "name": "api-service",
            "description": "REST API service",
            "stars": 5,
            "language": "Java",
            "last_updated": "2021-07-15"
        }
    ],
    "code_quality_score": 6,
    "skills_match": 75.3
}

# Expected Fraud Flags (minor concerns)
EXPECTED_FRAUD_FLAGS = [
    {
        "type": "EMPLOYMENT_GAP",
        "severity": "MINOR",
        "description": "15-month gap between CloudTech Solutions (ended Aug 2021) and DataSystems Corp (started Jan 2023)",
        "explanation": "Candidate explained: 'I took time off to care for a sick family member and do freelance work'"
    },
    {
        "type": "UNVERIFIED_EMPLOYMENT",
        "severity": "MINOR",
        "description": "Unable to verify employment at WebDev Inc - company no longer in business",
        "impact": "Cannot confirm earliest employment period"
    },
    {
        "type": "GITHUB_ACTIVITY_GAP",
        "severity": "MINOR",
        "description": "Very low GitHub activity in 2022 (only 12 commits) during claimed employment gap",
        "impact": "Aligns with candidate's explanation of personal time off"
    }
]

# Expected Risk Score
EXPECTED_RISK_SCORE = "YELLOW"

# Expected Report Summary
EXPECTED_REPORT_SUMMARY = """
Michael Rodriguez is a mid-level developer with generally verified employment history but 
some minor concerns. Recent employment at DataSystems Corp is fully verified with positive 
confirmation from HR. References provide mixed feedback, noting solid technical skills but 
areas for improvement in communication and proactivity. A 15-month employment gap between 
2021-2023 was explained as personal time off for family care and freelance work. GitHub 
activity is moderate and shows a corresponding gap in 2022. Earliest employment at WebDev 
Inc could not be verified as the company is no longer in business. Overall, the candidate 
appears legitimate but with some performance concerns noted by references.
"""

# Conversational Flow (with gap clarification)
CONVERSATIONAL_FLOW = [
    {
        "agent": "Hi Michael! Let's start by uploading your CV.",
        "candidate": "[uploads CV]",
        "agent_action": "extract_cv"
    },
    {
        "agent": "Thanks! I see you worked at DataSystems Corp from January 2023 to November 2024. Could you upload a pay stub from DataSystems Corp?",
        "candidate": "[uploads paystub]",
        "agent_action": "extract_paystub"
    },
    {
        "agent": "Great! Now I notice you worked at CloudTech Solutions until August 2021, but didn't start at DataSystems Corp until January 2023. That's about 15 months. Can you tell me what you were doing during that time?",
        "candidate": "I took time off to care for my mother who was ill, and I did some freelance consulting work during that period.",
        "agent_action": "record_explanation"
    },
    {
        "agent": "I understand, thank you for explaining. Do you have any documentation from your freelance work, like contracts or invoices?",
        "candidate": "I have some invoices but they're not very formal - it was mostly small projects for local businesses.",
        "agent_action": "record_explanation"
    },
    {
        "agent": "That's okay. Could you upload a pay stub from CloudTech Solutions to verify that employment?",
        "candidate": "I don't have any paystubs from that long ago, sorry.",
        "agent_action": "record_missing_document"
    },
    {
        "agent": "No problem, we'll verify directly with the company. Could you upload your diploma from State University?",
        "candidate": "[uploads diploma]",
        "agent_action": "extract_diploma"
    },
    {
        "agent": "Perfect! Here's what I have:\n\n- Employment at DataSystems Corp (2023-2024) - Verified with paystub\n- Employment gap (2021-2023) - Explained as family care and freelance work\n- Employment at CloudTech Solutions (2019-2021) - Will verify with HR\n- Employment at WebDev Inc (2017-2019) - Will verify with HR\n- BS in Computer Science from State University (2017) - Verified with diploma\n\nDoes this look correct?",
        "candidate": "Yes, that's right.",
        "agent_action": "finalize_collection"
    }
]
