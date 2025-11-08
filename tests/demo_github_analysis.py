"""Demo script showing GitHub profile analysis integration"""

import os
from datetime import datetime
from src.core.technical_profile_analyzer import TechnicalProfileAnalyzer
from src.database.models import db, VerificationSession, Candidate, GitHubAnalysisRecord
from src.api import create_app


def demo_github_analysis():
    """Demonstrate GitHub profile analysis with database storage"""
    
    print("\n" + "="*60)
    print("GitHub Profile Analysis Demo")
    print("="*60 + "\n")
    
    # Initialize analyzer
    analyzer = TechnicalProfileAnalyzer()
    
    # Example candidate with GitHub profile
    github_username = 'torvalds'
    claimed_skills = ['C', 'Linux', 'Git', 'Assembly', 'Python', 'JavaScript']
    
    print(f"Analyzing GitHub profile: {github_username}")
    print(f"Claimed skills: {', '.join(claimed_skills)}\n")
    
    # Perform analysis
    analysis = analyzer.analyze_github_profile(github_username, claimed_skills)
    
    # Display results
    print("="*60)
    print("ANALYSIS RESULTS")
    print("="*60 + "\n")
    
    if not analysis.profile_found:
        print(f"❌ Profile not found: {analysis.analysis_notes}")
        return
    
    print(f"✓ Profile Found: {analysis.profile_url}\n")
    
    print("📊 Repository Statistics:")
    print(f"  • Total Repositories: {analysis.total_repos}")
    print(f"  • Owned Repositories: {analysis.owned_repos}")
    print(f"  • Total Commits: {analysis.total_commits}")
    print(f"  • Commit Frequency: {analysis.commit_frequency} commits/month\n")
    
    print("💻 Language Distribution:")
    sorted_langs = sorted(analysis.languages.items(), key=lambda x: x[1], reverse=True)
    for lang, count in sorted_langs[:5]:
        print(f"  • {lang}: {count} repositories")
    print()
    
    print("📈 Recent Activity (last 6 months):")
    sorted_timeline = sorted(analysis.contribution_timeline.items(), reverse=True)[:6]
    for month, commits in sorted_timeline:
        print(f"  • {month}: {commits} commits")
    print()
    
    print(f"⭐ Code Quality Score: {analysis.code_quality_score}/10")
    
    # Interpret score
    if analysis.code_quality_score >= 8:
        quality_assessment = "Excellent - High quality repositories with good documentation"
    elif analysis.code_quality_score >= 6:
        quality_assessment = "Good - Solid projects with reasonable engagement"
    elif analysis.code_quality_score >= 4:
        quality_assessment = "Fair - Some activity but limited engagement"
    else:
        quality_assessment = "Limited - Minimal activity or engagement"
    
    print(f"  Assessment: {quality_assessment}\n")
    
    print("🎯 Skills Verification:")
    if analysis.skills_match:
        match_pct = analysis.skills_match.get('match_percentage', 0)
        matched = analysis.skills_match.get('matched_skills', [])
        unmatched = analysis.skills_match.get('unmatched_skills', [])
        
        print(f"  • Match Percentage: {match_pct}%")
        
        if matched:
            print(f"  • Verified Skills: {', '.join(matched)}")
        
        if unmatched:
            print(f"  • ⚠ Unverified Skills: {', '.join(unmatched)}")
            print(f"    (No evidence found in GitHub activity)")
    
    if analysis.mismatches:
        print(f"\n🚩 Potential Issues:")
        for mismatch in analysis.mismatches:
            print(f"  • {mismatch}")
    
    print("\n" + "="*60)
    print("FRAUD DETECTION ASSESSMENT")
    print("="*60 + "\n")
    
    # Fraud detection logic
    fraud_flags = []
    
    # Check for skill mismatches
    if analysis.skills_match:
        match_pct = analysis.skills_match.get('match_percentage', 0)
        if match_pct < 30:
            fraud_flags.append({
                'severity': 'CRITICAL',
                'type': 'TECHNICAL_MISMATCH',
                'description': f'Only {match_pct}% of claimed skills verified on GitHub'
            })
        elif match_pct < 60:
            fraud_flags.append({
                'severity': 'MODERATE',
                'type': 'TECHNICAL_MISMATCH',
                'description': f'{match_pct}% skill match - some claimed skills not evident'
            })
    
    # Check for low activity
    if analysis.commit_frequency < 1:
        fraud_flags.append({
            'severity': 'MODERATE',
            'type': 'TECHNICAL_MISMATCH',
            'description': f'Low GitHub activity ({analysis.commit_frequency} commits/month)'
        })
    
    # Check for low quality
    if analysis.code_quality_score < 4:
        fraud_flags.append({
            'severity': 'MINOR',
            'type': 'TECHNICAL_MISMATCH',
            'description': f'Low code quality score ({analysis.code_quality_score}/10)'
        })
    
    if fraud_flags:
        for flag in fraud_flags:
            severity_emoji = {'CRITICAL': '🔴', 'MODERATE': '🟡', 'MINOR': '🟢'}
            print(f"{severity_emoji[flag['severity']]} {flag['severity']}: {flag['description']}")
    else:
        print("✅ No fraud flags detected - Technical profile verified")
    
    print("\n" + "="*60)
    print("INTERVIEW RECOMMENDATIONS")
    print("="*60 + "\n")
    
    # Generate interview questions based on findings
    questions = []
    
    if analysis.skills_match:
        unmatched = analysis.skills_match.get('unmatched_skills', [])
        if unmatched:
            questions.append(
                f"Can you provide examples of projects where you used {', '.join(unmatched[:2])}? "
                "We didn't see evidence of these skills in your GitHub profile."
            )
    
    if analysis.commit_frequency < 2:
        questions.append(
            "Your GitHub shows limited recent activity. Can you explain where you've been "
            "doing most of your development work?"
        )
    
    if analysis.code_quality_score < 6:
        questions.append(
            "Can you walk us through your best project and explain your development process, "
            "testing approach, and documentation practices?"
        )
    
    # Add general technical questions
    if analysis.languages:
        top_lang = sorted(analysis.languages.items(), key=lambda x: x[1], reverse=True)[0][0]
        questions.append(
            f"We see you primarily work with {top_lang}. Can you describe a challenging "
            f"problem you solved using {top_lang}?"
        )
    
    for i, question in enumerate(questions, 1):
        print(f"{i}. {question}\n")
    
    print("="*60 + "\n")
    
    return analysis


def demo_database_storage():
    """Demonstrate storing GitHub analysis in database"""
    
    print("\n" + "="*60)
    print("Database Storage Demo")
    print("="*60 + "\n")
    
    # Create Flask app for database context
    app = create_app()
    
    with app.app_context():
        # Create test candidate and verification session
        candidate = Candidate(
            full_name="Linus Torvalds",
            email="linus@example.com"
        )
        db.session.add(candidate)
        db.session.flush()
        
        session = VerificationSession(
            candidate_id=candidate.id,
            status='VERIFICATION_IN_PROGRESS'
        )
        db.session.add(session)
        db.session.flush()
        
        # Perform GitHub analysis
        analyzer = TechnicalProfileAnalyzer()
        analysis = analyzer.analyze_github_profile('torvalds', ['C', 'Linux', 'Git'])
        
        # Store in database
        github_record = GitHubAnalysisRecord(
            verification_session_id=session.id,
            username=analysis.username,
            profile_found=analysis.profile_found,
            total_repos=analysis.total_repos,
            owned_repos=analysis.owned_repos,
            total_commits=analysis.total_commits,
            commit_frequency=analysis.commit_frequency,
            languages=analysis.languages,
            contribution_timeline=analysis.contribution_timeline,
            code_quality_score=analysis.code_quality_score,
            skills_match=analysis.skills_match,
            mismatches=analysis.mismatches,
            profile_url=analysis.profile_url,
            analysis_notes=analysis.analysis_notes
        )
        db.session.add(github_record)
        db.session.commit()
        
        print(f"✅ Stored GitHub analysis for {candidate.full_name}")
        print(f"   Session ID: {session.id}")
        print(f"   Analysis ID: {github_record.id}")
        print(f"   Code Quality Score: {github_record.code_quality_score}/10")
        print(f"   Profile URL: {github_record.profile_url}\n")
        
        # Retrieve and display
        retrieved = GitHubAnalysisRecord.query.filter_by(
            verification_session_id=session.id
        ).first()
        
        print(f"✅ Retrieved analysis from database:")
        print(f"   Username: {retrieved.username}")
        print(f"   Total Repos: {retrieved.total_repos}")
        print(f"   Languages: {list(retrieved.languages.keys())[:3]}")
        print(f"   Analyzed at: {retrieved.analyzed_at}")
        
        # Cleanup
        db.session.delete(github_record)
        db.session.delete(session)
        db.session.delete(candidate)
        db.session.commit()
        
        print(f"\n✅ Demo data cleaned up")


if __name__ == '__main__':
    try:
        # Run analysis demo
        demo_github_analysis()
        
        # Run database storage demo
        demo_database_storage()
        
        print("\n✅ All demos completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
