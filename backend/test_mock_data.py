#!/usr/bin/env python3
"""Test mock data system functionality"""

print("=" * 70)
print("MOCK DATA SYSTEM TEST")
print("=" * 70)

# Test 1: Load reference templates
print("\n1. Testing Reference Templates...")
print("-" * 70)
try:
    from services.mock_loader import load_reference_templates
    templates = load_reference_templates()
    
    print(f"[OK] Loaded {len(templates['templates'])} reference templates\n")
    
    for template in templates['templates']:
        print(f"Template: {template['id']}")
        print(f"  Weight: {template['weight'] * 100}%")
        print(f"  Rating: {template['performance_rating']}/10")
        print(f"  Would Rehire: {template['would_rehire']}")
        print(f"  Strengths: {', '.join(template['strengths'][:2])}")
        print(f"  Examples: {len(template['examples'])} available")
        print()
        
except Exception as e:
    print(f"[FAIL] {e}")

# Test 2: Load fraud scenarios
print("\n2. Testing Fraud Scenarios...")
print("-" * 70)
try:
    from services.mock_loader import load_fraud_scenarios
    scenarios = load_fraud_scenarios()
    
    print(f"[OK] Loaded {len(scenarios['scenarios'])} fraud scenarios\n")
    
    for scenario in scenarios['scenarios']:
        print(f"Scenario: {scenario['id']}")
        print(f"  Severity: {scenario['severity'].upper()}")
        print(f"  Claim: {scenario.get('resume_claim', scenario.get('employment_claim', 'N/A'))}")
        print()
        
except Exception as e:
    print(f"[FAIL] {e}")

# Test 3: Generate weighted responses
print("\n3. Testing Weighted Reference Responses...")
print("-" * 70)
try:
    from services.mock_loader import get_weighted_reference_response
    
    print("[OK] Generating 10 sample responses (should favor strong performers):\n")
    
    distribution = {"strong_performer": 0, "solid_contributor": 0, "performance_concerns": 0}
    
    for i in range(10):
        response = get_weighted_reference_response()
        rating = response['performance_rating']
        
        # Categorize based on rating
        if rating >= 8:
            category = "strong_performer"
        elif rating >= 7:
            category = "solid_contributor"
        else:
            category = "performance_concerns"
        
        distribution[category] += 1
        
        print(f"Response {i+1}:")
        print(f"  Rating: {rating}/10")
        print(f"  Would Rehire: {response['would_rehire']}")
        print(f"  Example: {response['specific_example'][:60]}...")
        print()
    
    print("Distribution (expected ~60% strong, 30% solid, 10% concerns):")
    for category, count in distribution.items():
        print(f"  {category}: {count}/10 ({count*10}%)")
    
except Exception as e:
    print(f"[FAIL] {e}")

# Test 4: Generate mock references
print("\n4. Testing Mock Reference Generation...")
print("-" * 70)
try:
    from services.mock_loader import generate_mock_references
    
    employment_history = [
        {"company": "TechCorp", "title": "Senior Engineer", "start": "2020-01", "end": "2024-01"},
        {"company": "StartupXYZ", "title": "Developer", "start": "2018-06", "end": "2019-12"}
    ]
    
    references = generate_mock_references(employment_history)
    
    print(f"[OK] Generated {len(references)} mock references\n")
    
    # Group by company
    by_company = {}
    for ref in references:
        company = ref['company']
        if company not in by_company:
            by_company[company] = []
        by_company[company].append(ref)
    
    for company, refs in by_company.items():
        print(f"{company}: {len(refs)} coworkers")
        
        # Show sample references
        for ref in refs[:3]:
            print(f"  - {ref['name']} ({ref['title']}, {ref['relationship']})")
        
        if len(refs) > 3:
            print(f"  ... and {len(refs) - 3} more")
        print()
    
except Exception as e:
    print(f"[FAIL] {e}")

# Test 5: Simulate outreach responses
print("\n5. Testing Outreach Response Simulation...")
print("-" * 70)
try:
    from services.mock_loader import simulate_outreach_responses
    
    # Use references from test 4
    responses = simulate_outreach_responses(references, response_rate=0.20)
    
    print(f"[OK] Simulated outreach to {len(references)} references\n")
    print(f"Response rate: {len(responses)}/{len(references)} ({len(responses)/len(references)*100:.1f}%)")
    print(f"Expected: ~20% response rate\n")
    
    # Show sample responses
    print("Sample responses:")
    for i, resp in enumerate(responses[:3]):
        print(f"\nResponse {i+1}:")
        print(f"  From: {resp['reference_name']} ({resp['reference_title']})")
        print(f"  Company: {resp['company']}")
        print(f"  Relationship: {resp['relationship']}")
        print(f"  Rating: {resp['performance_rating']}/10")
        print(f"  Would Rehire: {resp['would_rehire']}")
        print(f"  Strengths: {', '.join(resp['strengths'][:2])}")
    
    if len(responses) > 3:
        print(f"\n... and {len(responses) - 3} more responses")
    
except Exception as e:
    print(f"[FAIL] {e}")

# Test 6: Integration test
print("\n6. Integration Test: Full Mock Reference Flow...")
print("-" * 70)
try:
    print("[OK] Simulating complete reference check workflow:\n")
    
    # Step 1: Parse resume (simulated)
    candidate_name = "John Doe"
    employment_history = [
        {"company": "BigTech Inc", "title": "Senior Software Engineer", "start": "2020-01", "end": "2024-01"},
        {"company": "Startup Co", "title": "Full Stack Developer", "start": "2018-06", "end": "2019-12"}
    ]
    
    print(f"Candidate: {candidate_name}")
    print(f"Employment History: {len(employment_history)} positions\n")
    
    # Step 2: Generate mock coworkers
    all_references = generate_mock_references(employment_history)
    print(f"Step 1: Generated {len(all_references)} potential references")
    
    # Step 3: Simulate outreach
    responses = simulate_outreach_responses(all_references, response_rate=0.20)
    print(f"Step 2: Received {len(responses)} responses ({len(responses)/len(all_references)*100:.1f}%)")
    
    # Step 4: Analyze responses
    avg_rating = sum(r['performance_rating'] for r in responses) / len(responses)
    rehire_rate = sum(1 for r in responses if r['would_rehire']) / len(responses) * 100
    
    print(f"\nAnalysis:")
    print(f"  Average Rating: {avg_rating:.1f}/10")
    print(f"  Would Rehire: {rehire_rate:.0f}%")
    
    # Step 5: Categorize by company
    by_company = {}
    for resp in responses:
        company = resp['company']
        if company not in by_company:
            by_company[company] = []
        by_company[company].append(resp)
    
    print(f"\nResponses by Company:")
    for company, resps in by_company.items():
        avg = sum(r['performance_rating'] for r in resps) / len(resps)
        print(f"  {company}: {len(resps)} responses, avg rating {avg:.1f}/10")
    
    print("\n[OK] Mock data system working end-to-end!")
    
except Exception as e:
    print(f"[FAIL] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("MOCK DATA TEST COMPLETE")
print("=" * 70)
