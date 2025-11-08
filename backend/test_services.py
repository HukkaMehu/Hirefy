"""
Test script for GitHub API client and mock data system
Run from backend/ directory: python test_services.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_github_api():
    """Test GitHub API client"""
    print("\n=== Testing GitHub API ===")
    from services.github_api import analyze_github_profile
    
    # Test with a well-known GitHub user
    result = analyze_github_profile('torvalds')
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Username: {result['profile']['username']}")
        print(f"Name: {result['profile']['name']}")
        print(f"Public Repos: {result['profile']['public_repos']}")
        print(f"Followers: {result['profile']['followers']}")
        print(f"Total Commits: {result['activity']['total_commits']}")
        print(f"Languages: {result['repositories']['languages']}")
        print(f"Stars Received: {result['repositories']['stars_received']}")
    
    print("\n✓ GitHub API test completed")

def test_mock_loader():
    """Test mock data loader"""
    print("\n=== Testing Mock Data Loader ===")
    from services.mock_loader import (
        get_weighted_reference_response,
        generate_mock_references,
        simulate_outreach_responses
    )
    
    # Test weighted reference response
    print("\n1. Testing weighted reference response:")
    for i in range(3):
        response = get_weighted_reference_response()
        print(f"   Sample {i+1}: Rating={response['performance_rating']}, "
              f"Rehire={response['would_rehire']}, "
              f"Strengths={len(response['strengths'])}")
    
    # Test reference generation
    print("\n2. Testing reference generation:")
    employment_history = [
        {"company": "TestCorp"},
        {"company": "DevCompany"},
        {"company": "TechStartup"}
    ]
    refs = generate_mock_references(employment_history)
    print(f"   Generated {len(refs)} references from {len(employment_history)} companies")
    print(f"   Sample reference: {refs[0]['name']} - {refs[0]['title']} at {refs[0]['company']}")
    
    # Test outreach simulation
    print("\n3. Testing outreach simulation:")
    responses = simulate_outreach_responses(refs, response_rate=0.20)
    print(f"   {len(responses)} responses from {len(refs)} references ({len(responses)/len(refs)*100:.1f}% response rate)")
    if responses:
        print(f"   Sample response: {responses[0]['reference_name']} - Rating: {responses[0]['performance_rating']}")
    
    print("\n✓ Mock data loader test completed")

def test_fraud_scenarios():
    """Test fraud scenarios loading"""
    print("\n=== Testing Fraud Scenarios ===")
    from services.mock_loader import load_fraud_scenarios
    
    scenarios = load_fraud_scenarios()
    print(f"Loaded {len(scenarios['scenarios'])} fraud scenarios:")
    for scenario in scenarios['scenarios']:
        print(f"  - {scenario['id']}: {scenario['severity']} flag")
    
    print("\n✓ Fraud scenarios test completed")

if __name__ == "__main__":
    print("=" * 60)
    print("Backend Services Test Suite")
    print("=" * 60)
    
    try:
        test_mock_loader()
        test_fraud_scenarios()
        test_github_api()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
