"""Test technical profile analyzer functionality"""

import os
from src.core.technical_profile_analyzer import TechnicalProfileAnalyzer, GitHubAnalysis


def test_github_profile_analysis():
    """Test GitHub profile analysis with a real profile"""
    print("\n=== Testing GitHub Profile Analysis ===\n")
    
    # Initialize analyzer
    analyzer = TechnicalProfileAnalyzer()
    
    # Test with a well-known GitHub user (torvalds - creator of Linux)
    print("Analyzing GitHub profile: torvalds")
    claimed_skills = ['C', 'Linux', 'Git', 'Python', 'JavaScript']
    
    analysis = analyzer.analyze_github_profile('torvalds', claimed_skills)
    
    print(f"\nProfile Found: {analysis.profile_found}")
    print(f"Username: {analysis.username}")
    print(f"Profile URL: {analysis.profile_url}")
    print(f"Total Repositories: {analysis.total_repos}")
    print(f"Owned Repositories: {analysis.owned_repos}")
    print(f"Total Commits: {analysis.total_commits}")
    print(f"Commit Frequency (per month): {analysis.commit_frequency}")
    print(f"Code Quality Score: {analysis.code_quality_score}/10")
    
    print(f"\nLanguage Distribution:")
    for lang, count in sorted(analysis.languages.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {lang}: {count} repositories")
    
    print(f"\nContribution Timeline (recent months):")
    sorted_timeline = sorted(analysis.contribution_timeline.items(), reverse=True)[:6]
    for month, commits in sorted_timeline:
        print(f"  - {month}: {commits} commits")
    
    print(f"\nSkills Match:")
    if analysis.skills_match:
        print(f"  - Match Percentage: {analysis.skills_match.get('match_percentage', 0)}%")
        print(f"  - Matched Skills: {', '.join(analysis.skills_match.get('matched_skills', []))}")
        print(f"  - Unmatched Skills: {', '.join(analysis.skills_match.get('unmatched_skills', []))}")
        print(f"  - GitHub Languages: {', '.join(analysis.skills_match.get('github_languages', []))}")
    
    if analysis.mismatches:
        print(f"\nMismatches Detected:")
        for mismatch in analysis.mismatches:
            print(f"  - {mismatch}")
    
    print(f"\nAnalysis Notes: {analysis.analysis_notes}")
    
    # Test serialization
    print("\n=== Testing Serialization ===\n")
    analysis_dict = analysis.to_dict()
    print(f"Successfully serialized to dict with {len(analysis_dict)} fields")
    
    return analysis


def test_nonexistent_profile():
    """Test with a profile that doesn't exist"""
    print("\n=== Testing Non-Existent Profile ===\n")
    
    analyzer = TechnicalProfileAnalyzer()
    analysis = analyzer.analyze_github_profile('thisuserdoesnotexist12345xyz')
    
    print(f"Profile Found: {analysis.profile_found}")
    print(f"Analysis Notes: {analysis.analysis_notes}")
    
    assert not analysis.profile_found, "Should not find non-existent profile"
    print("✓ Correctly handled non-existent profile")


def test_skill_comparison():
    """Test skill comparison with a developer profile"""
    print("\n=== Testing Skill Comparison ===\n")
    
    analyzer = TechnicalProfileAnalyzer()
    
    # Test with a Python-focused developer
    print("Analyzing profile with claimed Python skills")
    claimed_skills = ['Python', 'JavaScript', 'TypeScript', 'React', 'Django']
    
    # Using 'gvanrossum' (creator of Python) as example
    analysis = analyzer.analyze_github_profile('gvanrossum', claimed_skills)
    
    if analysis.profile_found:
        print(f"\nProfile: {analysis.username}")
        print(f"Claimed Skills: {', '.join(claimed_skills)}")
        print(f"GitHub Languages: {', '.join(list(analysis.languages.keys())[:5])}")
        
        if analysis.skills_match:
            match_pct = analysis.skills_match.get('match_percentage', 0)
            print(f"Match Percentage: {match_pct}%")
            
            if match_pct < 50:
                print("⚠ Low skill match - potential mismatch detected")
            elif match_pct < 80:
                print("⚠ Moderate skill match")
            else:
                print("✓ High skill match")


def test_code_quality_scoring():
    """Test code quality scoring algorithm"""
    print("\n=== Testing Code Quality Scoring ===\n")
    
    analyzer = TechnicalProfileAnalyzer()
    
    # Test with profiles of varying quality
    test_users = [
        ('torvalds', 'High-quality profile (Linux creator)'),
        ('octocat', 'GitHub mascot account'),
    ]
    
    for username, description in test_users:
        analysis = analyzer.analyze_github_profile(username)
        if analysis.profile_found:
            print(f"\n{description}")
            print(f"  Username: {username}")
            print(f"  Code Quality Score: {analysis.code_quality_score}/10")
            print(f"  Total Repos: {analysis.total_repos}")
            print(f"  Owned Repos: {analysis.owned_repos}")


if __name__ == '__main__':
    print("=" * 60)
    print("Technical Profile Analyzer Test Suite")
    print("=" * 60)
    
    # Run tests
    try:
        test_github_profile_analysis()
        test_nonexistent_profile()
        test_skill_comparison()
        test_code_quality_scoring()
        
        print("\n" + "=" * 60)
        print("✓ All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
