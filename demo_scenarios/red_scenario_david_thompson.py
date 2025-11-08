"""
Red Scenario - David Thompson
Candidate with timeline conflicts, unverifiable credentials, GitHub activity mismatch
Expected Risk Score: RED
"""

# Candidate Profile
CANDIDATE_DATA = {
    "name": "David Thompson",
    "email": "david.thompson@email.com",
    "phone": "+1-555-0303",
    "github_username": "dthompson",
    "linkedin": "linkedin.com/in/davidthompson"
}

# CV Data (with inflated claims)
CV_DATA = {
    "employment_history": [
        {
            "company": "Elite Tech Corp",
            "title": "Lead Software Architect",
            "start_date": "2022-01-01",
            "end_date": "2024-10-31",
            "responsibilities": [
                "Architected enterprise-scale systems",
                "Led team of 15 engineers",
                "Designed microservices infrastructure",
                "Implemented AI/ML solutions"
            ],
            "technologies": ["Python", "Go", "Kubernetes", "TensorFlow", "AWS", "React"]
        },
        {
            "company": "InnovateSoft",
            "title": "Senior Full Stack Developer",
            "start_date": "2019-06-01",
            "end_date": "2021-12-31",
            "responsibilities": [
                "Built scalable web applications",
                "Mentored junior developers",
                "Optimized system performance"
            ],
            "technologies": ["Python", "React", "PostgreSQL", "Redis", "Docker"]
        },
        {
            "company": "CodeFactory",
            "title": "Software Engineer",
            "start_date": "2017-03-01",
            "end_date": "2019-05-31",
            "responsibilities": [
                "Developed backend services",
                "Implemented REST APIs",
                "Database design and optimization"
            ],
            "technologies": ["Java", "Spring", "MySQL", "AWS"]
        }
    ],
    "education": [
        {
            "institution": "Massachusetts Institute of Technology",
            "degree": "Master of Science",
            "major": "Computer Science",
            "graduation_date": "2017-05-15",
            "gpa": "3.9"
        },
        {
            "institution": "Stanford University",
            "degree": "Bachelor of Science",
            "major": "Computer Science",
            "graduation_date": "2015-06-10",
            "gpa": "3.8"
        }
    ],
    "skills": ["Python", "Go", "Java", "React", "Kubernetes", "TensorFlow", "AWS", "PostgreSQL", "Redis"],
    "certifications": ["AWS Solutions Architect Professional", "Google Cloud Professional"]
}

# Supporting Documents (conflicts with CV)
PAYSTUB_DATA = [
    {
        "company": "Elite Tech Corp",
        "employee_name": "David Thompson",
        "title": "Software Developer",  # CONFLICT: CV says "Lead Software Architect"
        "pay_period": "2024-10-01 to 2024-10-15",
        "gross_pay": "$5,500.00"  # Lower than expected for architect role
    },
    {
        "company": "InnovateSoft",
        "employee_name": "David Thompson",
        "title": "Junior Developer",  # CONFLICT: CV says "Senior Full Stack Developer"
        "pay_period": "2021-12-01 to 2021-12-15",
        "gross_pay": "$3,800.00"
    }
]

# Diploma Data (conflicts with CV)
DIPLOMA_DATA = {
    "institution": "State College",  # CONFLICT: CV says MIT
    "degree": "Bachelor of Science",  # CONFLICT: CV claims MS from MIT
    "major": "Information Technology",  # CONFLICT: CV says Computer Science
    "graduation_date": "May 15, 2016",  # CONFLICT: Different date
    "honors": None
}

# HR Verification Results (major discrepancies)
HR_VERIFICATION_RESULTS = [
    {
        "company": "Elite Tech Corp",
        "verified": True,
        "title_confirmed": "Software Developer",  # NOT Lead Architect
        "dates_confirmed": "March 2022 - October 2024",  # Started later than claimed
        "eligible_for_rehire": "No",
        "hr_contact": "Susan Miller, HR Manager",
        "notes": "Performance issues, did not hold leadership role"
    },
    {
        "company": "InnovateSoft",
        "verified": True,
        "title_confirmed": "Junior Developer",  # NOT Senior Full Stack
        "dates_confirmed": "August 2019 - November 2021",  # Different dates
        "eligible_for_rehire": "No",
        "hr_contact": "Mark Johnson, HR Director",
        "notes": "Left on bad terms, attendance issues"
    },
    {
        "company": "CodeFactory",
        "verified": False,
        "reason": "No record of employment found",
        "hr_contact": "Rachel Green, HR Manager",
        "notes": "Searched thoroughly, no David Thompson in our records"
    }
]

# Reference Check Results (negative/suspicious)
REFERENCE_RESULTS = [
    {
        "name": "John Smith",
        "relationship": "Claims to be former manager at Elite Tech Corp",
        "overlap_verified": False,  # FRAUD: This person doesn't exist at the company
        "feedback": {
            "performance": "Excellent",
            "technical_skills": "Outstanding",
            "collaboration": "Great team player",
            "strengths": "Everything",
            "areas_for_improvement": "None",
            "would_rehire": True
        },
        "quotes": [
            "David was amazing",
            "Best developer I ever worked with"
        ],
        "verification_note": "Elite Tech Corp HR confirmed no John Smith ever worked there"
    },
    {
        "name": "Emily Davis",
        "relationship": "Claims to be colleague at InnovateSoft",
        "overlap_verified": False,  # Could not reach
        "feedback": None,
        "verification_note": "Phone number disconnected, email bounced"
    }
]

# GitHub Analysis Results (minimal activity, doesn't match claims)
GITHUB_ANALYSIS = {
    "username": "dthompson",
    "profile_found": True,
    "total_repos": 8,
    "owned_repos": 3,
    "contributed_repos": 5,
    "total_commits": 127,  # Very low for claimed experience
    "commit_timeline": {
        "2017": 8,
        "2018": 15,
        "2019": 23,
        "2020": 31,
        "2021": 18,
        "2022": 12,
        "2023": 14,
        "2024": 6
    },
    "languages": {
        "JavaScript": 45.2,  # CONFLICT: CV emphasizes Python/Go
        "HTML": 28.3,
        "CSS": 15.1,
        "Python": 8.4,  # Very low despite claiming expertise
        "Other": 3.0
    },
    "activity_during_employment": {
        "Elite Tech Corp (2022-2024)": "Very low activity - 32 commits",
        "InnovateSoft (2019-2021)": "Low activity - 72 commits",
        "CodeFactory (2017-2019)": "Very low activity - 23 commits"
    },
    "notable_projects": [
        {
            "name": "todo-app",
            "description": "Simple todo list application",
            "stars": 2,
            "language": "JavaScript",
            "last_updated": "2023-05-10"
        },
        {
            "name": "calculator",
            "description": "Basic calculator",
            "stars": 0,
            "language": "HTML",
            "last_updated": "2022-03-15"
        }
    ],
    "code_quality_score": 3,  # Very low
    "skills_match": 28.5,  # Major mismatch
    "red_flags": [
        "No evidence of Kubernetes, TensorFlow, or Go projects",
        "No repositories showing architecture or leadership",
        "Projects are basic/tutorial level",
        "Very low commit frequency for claimed senior roles"
    ]
}

# Expected Fraud Flags (multiple critical issues)
EXPECTED_FRAUD_FLAGS = [
    {
        "type": "TITLE_INFLATION",
        "severity": "CRITICAL",
        "description": "CV claims 'Lead Software Architect' at Elite Tech Corp, but HR confirmed title was 'Software Developer'",
        "evidence": "Paystub also shows 'Software Developer', not architect role"
    },
    {
        "type": "TITLE_INFLATION",
        "severity": "CRITICAL",
        "description": "CV claims 'Senior Full Stack Developer' at InnovateSoft, but HR confirmed title was 'Junior Developer'",
        "evidence": "Paystub confirms 'Junior Developer' title"
    },
    {
        "type": "TIMELINE_CONFLICT",
        "severity": "CRITICAL",
        "description": "CV claims started at Elite Tech Corp in January 2022, but HR confirmed start date was March 2022",
        "impact": "2-month discrepancy"
    },
    {
        "type": "UNVERIFIED_EMPLOYMENT",
        "severity": "CRITICAL",
        "description": "CodeFactory HR has no record of David Thompson ever working there",
        "impact": "Entire employment period (2017-2019) appears fabricated"
    },
    {
        "type": "EDUCATION_FRAUD",
        "severity": "CRITICAL",
        "description": "CV claims MS from MIT and BS from Stanford, but diploma shows BS from State College in Information Technology",
        "impact": "Completely fabricated graduate degree and undergraduate institution"
    },
    {
        "type": "FAKE_REFERENCE",
        "severity": "CRITICAL",
        "description": "Reference 'John Smith' claims to be manager at Elite Tech Corp, but HR confirmed no such person ever worked there",
        "impact": "Fabricated reference providing glowing but false feedback"
    },
    {
        "type": "TECHNICAL_MISREPRESENTATION",
        "severity": "CRITICAL",
        "description": "CV claims expertise in Python, Go, Kubernetes, TensorFlow, but GitHub shows minimal Python (8.4%), no Go, and only basic JavaScript projects",
        "impact": "No evidence of claimed technical skills or architecture experience"
    },
    {
        "type": "GITHUB_ACTIVITY_MISMATCH",
        "severity": "MODERATE",
        "description": "Only 127 total commits over 7+ years, with basic tutorial-level projects",
        "impact": "Activity level inconsistent with claimed senior/lead roles"
    },
    {
        "type": "INELIGIBLE_FOR_REHIRE",
        "severity": "MODERATE",
        "description": "Both verified employers (Elite Tech Corp and InnovateSoft) marked candidate as not eligible for rehire",
        "impact": "Performance and attendance issues noted"
    }
]

# Expected Risk Score
EXPECTED_RISK_SCORE = "RED"

# Expected Report Summary
EXPECTED_REPORT_SUMMARY = """
CRITICAL CONCERNS IDENTIFIED - NOT RECOMMENDED FOR HIRE

David Thompson's verification revealed multiple critical fraud flags and misrepresentations. 
The candidate significantly inflated job titles (claiming 'Lead Software Architect' when 
actually employed as 'Software Developer', and 'Senior Full Stack Developer' when actually 
'Junior Developer'). Education credentials are fraudulent - CV claims MS from MIT and BS 
from Stanford, but diploma shows BS from State College. One employment period at CodeFactory 
appears completely fabricated with no HR records found. A provided reference was verified 
as fake - the person never worked at the claimed company. GitHub analysis shows minimal 
activity (127 commits over 7 years) with only basic tutorial-level projects, contradicting 
claims of senior architecture experience. No evidence of claimed expertise in Python, Go, 
Kubernetes, or TensorFlow. Both verified employers marked candidate as ineligible for rehire 
due to performance and attendance issues. This candidate demonstrates a pattern of systematic 
misrepresentation and should not be considered for employment.
"""

# Conversational Flow (with conflicts)
CONVERSATIONAL_FLOW = [
    {
        "agent": "Hi David! Let's get started. Please upload your CV.",
        "candidate": "[uploads CV]",
        "agent_action": "extract_cv"
    },
    {
        "agent": "Thanks! I see you worked as Lead Software Architect at Elite Tech Corp. Could you upload a recent pay stub?",
        "candidate": "[uploads paystub]",
        "agent_action": "extract_paystub"
    },
    {
        "agent": "I notice something - your CV says you were 'Lead Software Architect' but this pay stub shows 'Software Developer'. Which is correct?",
        "candidate": "Oh, I was promoted to Lead Architect but the payroll system wasn't updated yet. My actual role was architect.",
        "agent_action": "record_conflict_explanation"
    },
    {
        "agent": "I see. Could you upload a pay stub from InnovateSoft?",
        "candidate": "[uploads paystub]",
        "agent_action": "extract_paystub"
    },
    {
        "agent": "Your CV says 'Senior Full Stack Developer' at InnovateSoft, but this pay stub shows 'Junior Developer'. Can you explain?",
        "candidate": "I started as junior but was promoted to senior. This must be an old pay stub.",
        "agent_action": "record_conflict_explanation"
    },
    {
        "agent": "Could you upload your diploma? I see you have an MS from MIT.",
        "candidate": "[uploads diploma]",
        "agent_action": "extract_diploma"
    },
    {
        "agent": "This diploma shows a BS from State College, but your CV says MS from MIT and BS from Stanford. Can you explain?",
        "candidate": "Oh, I must have uploaded the wrong file. Let me find my MIT diploma... Actually, I can't find it right now. I'll send it later.",
        "agent_action": "record_missing_document"
    },
    {
        "agent": "Okay. Let me summarize what I have:\n\n- Employment at Elite Tech Corp - Title discrepancy noted\n- Employment at InnovateSoft - Title discrepancy noted\n- Employment at CodeFactory - No documentation provided\n- Education credentials - Discrepancies between CV and diploma\n\nWe'll proceed with verification, but these inconsistencies will need to be resolved.",
        "candidate": "Sure, no problem.",
        "agent_action": "finalize_collection_with_flags"
    }
]
