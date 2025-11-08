"""Technical profile analyzer for GitHub and portfolio analysis"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from collections import Counter
import re


class GitHubAnalysis:
    """Data model for GitHub analysis results"""
    
    def __init__(
        self,
        username: str,
        profile_found: bool = False,
        total_repos: int = 0,
        owned_repos: int = 0,
        total_commits: int = 0,
        commit_frequency: float = 0.0,
        languages: Dict[str, int] = None,
        contribution_timeline: Dict[str, int] = None,
        code_quality_score: int = 0,
        skills_match: Dict[str, Any] = None,
        mismatches: List[str] = None,
        profile_url: Optional[str] = None,
        analysis_notes: str = ""
    ):
        self.username = username
        self.profile_found = profile_found
        self.total_repos = total_repos
        self.owned_repos = owned_repos
        self.total_commits = total_commits
        self.commit_frequency = commit_frequency
        self.languages = languages or {}
        self.contribution_timeline = contribution_timeline or {}
        self.code_quality_score = code_quality_score
        self.skills_match = skills_match or {}
        self.mismatches = mismatches or []
        self.profile_url = profile_url
        self.analysis_notes = analysis_notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'username': self.username,
            'profile_found': self.profile_found,
            'total_repos': self.total_repos,
            'owned_repos': self.owned_repos,
            'total_commits': self.total_commits,
            'commit_frequency': self.commit_frequency,
            'languages': self.languages,
            'contribution_timeline': self.contribution_timeline,
            'code_quality_score': self.code_quality_score,
            'skills_match': self.skills_match,
            'mismatches': self.mismatches,
            'profile_url': self.profile_url,
            'analysis_notes': self.analysis_notes
        }


class TechnicalProfileAnalyzer:
    """Analyzes GitHub profiles and technical contributions"""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize the analyzer with optional GitHub token for higher rate limits
        
        Args:
            github_token: GitHub personal access token (optional)
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json'
        }
        if self.github_token:
            self.headers['Authorization'] = f'token {self.github_token}'
    
    def analyze_github_profile(
        self,
        username: str,
        claimed_skills: List[str] = None
    ) -> GitHubAnalysis:
        """
        Analyze a GitHub profile and compare against claimed skills
        
        Args:
            username: GitHub username
            claimed_skills: List of skills claimed by candidate
            
        Returns:
            GitHubAnalysis object with analysis results
        """
        claimed_skills = claimed_skills or []
        
        try:
            # Get user profile
            user_data = self._get_user_profile(username)
            if not user_data:
                return GitHubAnalysis(
                    username=username,
                    profile_found=False,
                    analysis_notes="GitHub profile not found"
                )
            
            # Get repositories
            repos = self._get_user_repositories(username)
            
            # Analyze repositories
            language_stats = self._calculate_language_distribution(repos)
            contribution_timeline = self._calculate_contribution_timeline(username, repos)
            commit_frequency = self._calculate_commit_frequency(contribution_timeline)
            total_commits = sum(contribution_timeline.values())
            
            # Calculate code quality score
            code_quality_score = self._calculate_code_quality_score(repos)
            
            # Compare skills
            skills_match, mismatches = self._compare_skills_against_activity(
                claimed_skills,
                language_stats,
                repos
            )
            
            return GitHubAnalysis(
                username=username,
                profile_found=True,
                total_repos=len(repos),
                owned_repos=len([r for r in repos if not r.get('fork', False)]),
                total_commits=total_commits,
                commit_frequency=commit_frequency,
                languages=language_stats,
                contribution_timeline=contribution_timeline,
                code_quality_score=code_quality_score,
                skills_match=skills_match,
                mismatches=mismatches,
                profile_url=f"https://github.com/{username}",
                analysis_notes="Analysis completed successfully"
            )
            
        except Exception as e:
            return GitHubAnalysis(
                username=username,
                profile_found=False,
                analysis_notes=f"Error analyzing profile: {str(e)}"
            )
    
    def _get_user_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get GitHub user profile data"""
        try:
            response = requests.get(
                f"{self.base_url}/users/{username}",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception:
            return None
    
    def _get_user_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Get all public repositories for a user"""
        repos = []
        page = 1
        per_page = 100
        
        try:
            while True:
                response = requests.get(
                    f"{self.base_url}/users/{username}/repos",
                    headers=self.headers,
                    params={'page': page, 'per_page': per_page, 'sort': 'updated'},
                    timeout=10
                )
                
                if response.status_code != 200:
                    break
                
                page_repos = response.json()
                if not page_repos:
                    break
                
                repos.extend(page_repos)
                
                # Limit to first 100 repos for performance
                if len(repos) >= 100:
                    repos = repos[:100]
                    break
                
                page += 1
                
            return repos
        except Exception:
            return repos
    
    def _calculate_language_distribution(
        self,
        repos: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate language distribution across repositories"""
        language_counts = Counter()
        
        for repo in repos:
            # Skip forks for language analysis
            if repo.get('fork', False):
                continue
            
            language = repo.get('language')
            if language:
                language_counts[language] += 1
        
        return dict(language_counts)
    
    def _calculate_contribution_timeline(
        self,
        username: str,
        repos: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Calculate contribution timeline by analyzing commit activity
        Returns dict with year-month keys and commit counts
        """
        timeline = {}
        
        # Analyze owned repos (not forks)
        owned_repos = [r for r in repos if not r.get('fork', False)][:10]  # Limit to 10 most recent
        
        for repo in owned_repos:
            try:
                # Get commits for this repo
                commits_url = f"{self.base_url}/repos/{username}/{repo['name']}/commits"
                response = requests.get(
                    commits_url,
                    headers=self.headers,
                    params={'author': username, 'per_page': 100},
                    timeout=10
                )
                
                if response.status_code == 200:
                    commits = response.json()
                    for commit in commits:
                        try:
                            commit_date = commit['commit']['author']['date']
                            # Parse date and extract year-month
                            dt = datetime.fromisoformat(commit_date.replace('Z', '+00:00'))
                            year_month = dt.strftime('%Y-%m')
                            timeline[year_month] = timeline.get(year_month, 0) + 1
                        except (KeyError, ValueError):
                            continue
            except Exception:
                continue
        
        return timeline
    
    def _calculate_commit_frequency(self, timeline: Dict[str, int]) -> float:
        """
        Calculate average commits per month
        
        Args:
            timeline: Dict with year-month keys and commit counts
            
        Returns:
            Average commits per month
        """
        if not timeline:
            return 0.0
        
        total_commits = sum(timeline.values())
        num_months = len(timeline)
        
        if num_months == 0:
            return 0.0
        
        return round(total_commits / num_months, 2)
    
    def _calculate_code_quality_score(self, repos: List[Dict[str, Any]]) -> int:
        """
        Calculate code quality score (1-10) based on repository metrics
        
        Scoring factors:
        - Repository documentation (README, wiki)
        - Star count and engagement
        - Repository structure and organization
        - Consistent activity
        - Non-fork ratio
        """
        if not repos:
            return 0
        
        score = 0
        owned_repos = [r for r in repos if not r.get('fork', False)]
        
        if not owned_repos:
            return 1  # Minimum score if only forks
        
        # Factor 1: Documentation (0-3 points)
        repos_with_readme = sum(1 for r in owned_repos if r.get('has_wiki') or r.get('description'))
        doc_score = min(3, int((repos_with_readme / len(owned_repos)) * 3))
        score += doc_score
        
        # Factor 2: Engagement (0-3 points)
        total_stars = sum(r.get('stargazers_count', 0) for r in owned_repos)
        if total_stars > 100:
            score += 3
        elif total_stars > 20:
            score += 2
        elif total_stars > 5:
            score += 1
        
        # Factor 3: Repository quality (0-2 points)
        avg_size = sum(r.get('size', 0) for r in owned_repos) / len(owned_repos) if owned_repos else 0
        if avg_size > 1000:  # Substantial projects
            score += 2
        elif avg_size > 100:
            score += 1
        
        # Factor 4: Activity and maintenance (0-2 points)
        recently_updated = sum(
            1 for r in owned_repos
            if self._is_recently_updated(r.get('updated_at'))
        )
        if recently_updated / len(owned_repos) > 0.5:
            score += 2
        elif recently_updated / len(owned_repos) > 0.2:
            score += 1
        
        return min(10, max(1, score))  # Ensure score is between 1-10
    
    def _is_recently_updated(self, updated_at: Optional[str]) -> bool:
        """Check if repository was updated in the last 6 months"""
        if not updated_at:
            return False
        
        try:
            update_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            six_months_ago = datetime.now(update_date.tzinfo) - timedelta(days=180)
            return update_date > six_months_ago
        except (ValueError, TypeError):
            return False
    
    def _compare_skills_against_activity(
        self,
        claimed_skills: List[str],
        language_stats: Dict[str, int],
        repos: List[Dict[str, Any]]
    ) -> tuple[Dict[str, Any], List[str]]:
        """
        Compare claimed skills against actual GitHub activity
        
        Returns:
            Tuple of (skills_match dict, list of mismatches)
        """
        # Normalize skills and languages for comparison
        normalized_skills = [self._normalize_skill(skill) for skill in claimed_skills]
        normalized_languages = {self._normalize_skill(lang): count for lang, count in language_stats.items()}
        
        # Find matches
        matched_skills = []
        unmatched_skills = []
        
        for skill in normalized_skills:
            if skill in normalized_languages:
                matched_skills.append(skill)
            else:
                # Check if skill appears in repo descriptions or topics
                if self._skill_in_repos(skill, repos):
                    matched_skills.append(skill)
                else:
                    unmatched_skills.append(skill)
        
        # Calculate match percentage
        match_percentage = 0
        if normalized_skills:
            match_percentage = round((len(matched_skills) / len(normalized_skills)) * 100, 1)
        
        skills_match = {
            'claimed_skills': claimed_skills,
            'matched_skills': matched_skills,
            'unmatched_skills': unmatched_skills,
            'match_percentage': match_percentage,
            'github_languages': list(language_stats.keys())
        }
        
        # Generate mismatch descriptions
        mismatches = []
        if unmatched_skills:
            mismatches.append(
                f"No evidence found for claimed skills: {', '.join(unmatched_skills)}"
            )
        
        return skills_match, mismatches
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name for comparison"""
        # Convert to lowercase and remove special characters
        normalized = re.sub(r'[^a-z0-9]', '', skill.lower())
        
        # Map common variations
        skill_mappings = {
            'js': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'golang': 'go',
            'reactjs': 'react',
            'nodejs': 'node',
            'vuejs': 'vue',
            'nextjs': 'next',
        }
        
        return skill_mappings.get(normalized, normalized)
    
    def _skill_in_repos(self, skill: str, repos: List[Dict[str, Any]]) -> bool:
        """Check if skill appears in repository descriptions or topics"""
        for repo in repos:
            # Check description
            description = repo.get('description', '').lower()
            if skill in description:
                return True
            
            # Check topics
            topics = repo.get('topics', [])
            if any(skill in topic.lower() for topic in topics):
                return True
        
        return False
