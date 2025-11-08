#!/usr/bin/env python3
"""Test GitHub API integration"""

print("=" * 70)
print("GITHUB API INTEGRATION TEST")
print("=" * 70)

# Test 1: Module loading
print("\n1. Testing GitHub API module import...")
try:
    from services.github_api import analyze_github_profile
    print("[OK] GitHub API module loaded successfully")
except Exception as e:
    print(f"[FAIL] {e}")
    exit(1)

# Test 2: Analyze a real public GitHub profile
print("\n2. Testing GitHub profile analysis (using 'torvalds')...")
print("-" * 70)
try:
    result = analyze_github_profile('torvalds')
    
    if 'error' in result:
        print(f"[WARNING] API returned error: {result['error']}")
    else:
        print("[OK] Successfully retrieved GitHub profile data\n")
        
        # Profile info
        if 'profile' in result:
            profile = result['profile']
            print("Profile Information:")
            print(f"  Username: {profile.get('username')}")
            print(f"  Name: {profile.get('name')}")
            print(f"  Public Repos: {profile.get('public_repos')}")
            print(f"  Followers: {profile.get('followers')}")
            print(f"  Account Created: {profile.get('created_at', 'N/A')[:10]}")
            if profile.get('bio'):
                print(f"  Bio: {profile['bio'][:60]}...")
        
        # Repository info
        if 'repositories' in result:
            repos = result['repositories']
            print("\nRepository Analysis:")
            print(f"  Total Repos: {repos.get('total')}")
            print(f"  Original: {repos.get('original')}")
            print(f"  Forked: {repos.get('forked')}")
            print(f"  Stars Received: {repos.get('stars_received')}")
            
            if repos.get('languages'):
                print(f"  Top Languages:")
                sorted_langs = sorted(repos['languages'].items(), key=lambda x: x[1], reverse=True)
                for lang, count in sorted_langs[:5]:
                    print(f"    - {lang}: {count} repos")
        
        # Activity info
        if 'activity' in result:
            activity = result['activity']
            print("\nActivity:")
            print(f"  Total Commits (sample): {activity.get('total_commits')}")
            print(f"  Account Age: {activity.get('account_created_year')}")
    
except Exception as e:
    print(f"[FAIL] Error analyzing profile: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Test non-existent user
print("\n3. Testing error handling (non-existent user)...")
print("-" * 70)
try:
    result = analyze_github_profile('this-user-definitely-does-not-exist-12345')
    
    if 'error' in result:
        print(f"[OK] Properly handled missing user: {result['error']}")
    else:
        print("[WARNING] Expected error for non-existent user")
        
except Exception as e:
    print(f"[FAIL] {e}")

# Test 4: Test rate limiting awareness
print("\n4. Checking rate limit status...")
print("-" * 70)
try:
    import requests
    from config import get_settings
    
    settings = get_settings()
    headers = {}
    if settings.github_token:
        headers['Authorization'] = f'token {settings.github_token}'
        print("[INFO] Using GitHub token for authentication")
    else:
        print("[INFO] No GitHub token - using unauthenticated requests")
        print("       (Limited to 60 requests/hour)")
    
    response = requests.get('https://api.github.com/rate_limit', headers=headers)
    if response.status_code == 200:
        data = response.json()
        core = data.get('resources', {}).get('core', {})
        remaining = core.get('remaining', 'unknown')
        limit = core.get('limit', 'unknown')
        print(f"\n[OK] Rate Limit Status: {remaining}/{limit} requests remaining")
    else:
        print(f"[WARNING] Could not check rate limit: {response.status_code}")
        
except Exception as e:
    print(f"[WARNING] Rate limit check failed: {e}")

print("\n" + "=" * 70)
print("GITHUB API TEST COMPLETE")
print("=" * 70)
