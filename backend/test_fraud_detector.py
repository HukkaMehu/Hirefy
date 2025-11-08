from agents.fraud_detector import FraudDetector
from services.github_api import analyze_github_profile
from services.mock_loader import generate_mock_references, simulate_outreach_responses

print("="*60)
print("FRAUD DETECTOR TEST SUITE")
print("="*60)

detector = FraudDetector()

# Test 1: Green scenario - Skills match GitHub
print("\n[Test 1: Green Scenario - Matching Skills]")
resume_data_green = {
    "name": "Good Candidate",
    "skills": ["C", "Assembly", "Linux"],  # Matches torvalds' repos
    "employment_history": [
        {"company": "TechCorp", "title": "Engineer", "start_date": "2020-01", "end_date": "2024-01", "description": "Built stuff"}
    ]
}

github_data_torvalds = analyze_github_profile("torvalds")  # Has C code
refs_good = simulate_outreach_responses(generate_mock_references([{"company": "TechCorp"}]))

result1 = detector.analyze(resume_data_green, github_data_torvalds, refs_good)
print(f"[+] Risk Level: {result1['risk_level']}")
print(f"[+] Total Flags: {len(result1['flags'])}")
print(f"[+] Flag Breakdown: {result1['flag_count']}")
print(f"[+] Summary: {result1['summary']}")

# Test 2: Red scenario - Python claimed but GitHub shows C only
print("\n[Test 2: Red Scenario - Skill Mismatch]")
resume_data_fraud = {
    "name": "Fraud Candidate",
    "skills": ["Python", "Django", "Machine Learning"],  # Claims Python but torvalds has C
    "employment_history": [
        {"company": "FakeCorp", "title": "Senior Python Engineer", "start_date": "2020-01", "end_date": "2024-01", "description": "Python expert"}
    ]
}

result2 = detector.analyze(resume_data_fraud, github_data_torvalds, refs_good)
print(f"[+] Risk Level: {result2['risk_level']}")
print(f"[+] Total Flags: {len(result2['flags'])}")
print(f"[+] Flag Breakdown: {result2['flag_count']}")
print("[+] Detected Issues:")
for flag in result2['flags']:
    print(f"  - [{flag['severity'].upper()}] {flag['message']}")

# Test 3: Yellow scenario - Employment gap
print("\n[Test 3: Yellow Scenario - Employment Gap]")
resume_data_gap = {
    "name": "Gap Candidate",
    "skills": ["C"],
    "employment_history": [
        {"company": "Company A", "title": "Engineer", "start_date": "2018-01", "end_date": "2019-06", "description": "First job"},
        {"company": "Company B", "title": "Engineer", "start_date": "2020-03", "end_date": "2024-01", "description": "After gap"}
    ]
}

result3 = detector.analyze(resume_data_gap, github_data_torvalds, refs_good)
print(f"[+] Risk Level: {result3['risk_level']}")
print(f"[+] Total Flags: {len(result3['flags'])}")
print(f"[+] Flag Breakdown: {result3['flag_count']}")
if result3['flags']:
    print("[+] Detected Issues:")
    for flag in result3['flags']:
        print(f"  - [{flag['severity'].upper()}] {flag['message']}")

# Test 4: Test with JavaScript user
print("\n[Test 4: JavaScript Developer - Real GitHub Profile]")
resume_data_js = {
    "name": "JS Developer",
    "skills": ["JavaScript", "TypeScript", "React"],
    "employment_history": [
        {"company": "WebCorp", "title": "Frontend Dev", "start_date": "2020-01", "end_date": "2024-01", "description": "Built web apps"}
    ]
}

github_data_js = analyze_github_profile("gaearon")  # React core team member - has JS/TS
refs_js = simulate_outreach_responses(generate_mock_references([{"company": "WebCorp"}]))

result4 = detector.analyze(resume_data_js, github_data_js, refs_js)
print(f"[+] Risk Level: {result4['risk_level']}")
print(f"[+] Total Flags: {len(result4['flags'])}")
print(f"[+] Flag Breakdown: {result4['flag_count']}")
print(f"[+] Summary: {result4['summary']}")

print("\n" + "="*60)
print("ALL FRAUD DETECTOR TESTS COMPLETE!")
print("="*60)
