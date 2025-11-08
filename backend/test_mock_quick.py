#!/usr/bin/env python3
"""Quick test of mock data generation"""

from services.mock_loader import (
    generate_mock_references,
    simulate_outreach_responses,
    get_weighted_reference_response
)

print("QUICK MOCK DATA TEST")
print("=" * 60)

# Example employment history
jobs = [
    {"company": "Google", "title": "Senior Engineer"},
    {"company": "Meta", "title": "Software Engineer"}
]

# Generate references
print("\n1. Generating mock coworkers...")
refs = generate_mock_references(jobs)
print(f"   Created {len(refs)} references across {len(jobs)} companies")

# Simulate responses
print("\n2. Simulating 20% response rate...")
responses = simulate_outreach_responses(refs, response_rate=0.20)
print(f"   Got {len(responses)} responses from {len(refs)} contacts")
print(f"   Actual rate: {len(responses)/len(refs)*100:.1f}%")

# Analyze
print("\n3. Sample responses:")
for i, r in enumerate(responses[:3], 1):
    print(f"\n   Response {i}:")
    print(f"   Name: {r['reference_name']}")
    print(f"   Title: {r['reference_title']} at {r['company']}")
    print(f"   Rating: {r['performance_rating']}/10")
    print(f"   Would Rehire: {r['would_rehire']}")
    print(f"   Example: {r['specific_example'][:60]}...")

print("\n" + "=" * 60)
print("✓ Mock data system working!")
