import requests
from typing import Optional
from datetime import datetime
from collections import defaultdict
from config import get_settings

settings = get_settings()

def analyze_github_profile(username: str) -> dict:
    """
    Analyze GitHub profile using REST API
    Returns profile, repos, languages, commits, activity timeline
    """
    headers = {}
    if settings.github_token:
        headers['Authorization'] = f'token {settings.github_token}'
    
    try:
        # Get user profile
        user_response = requests.get(
            f'https://api.github.com/users/{username}',
            headers=headers,
            timeout=10
        )
        
        if user_response.status_code == 404:
            return {'error': 'GitHub user not found'}
        
        user = user_response.json()
        
        # Get repositories
        repos_response = requests.get(
            f'https://api.github.com/users/{username}/repos?per_page=100&sort=updated',
            headers=headers,
            timeout=10
        )
        
        if repos_response.status_code != 200:
            return {'error': f'Failed to fetch repositories: {repos_response.status_code}'}
        
        repos = repos_response.json()
        
        if not isinstance(repos, list):
            return {'error': 'Invalid response from GitHub API'}
        
        # Analyze repositories
        languages = defaultdict(int)
        total_stars = 0
        original_repos = 0
        forked_repos = 0
        
        for repo in repos[:30]:  # Limit to 30 most recent
            if repo.get('fork'):
                forked_repos += 1
            else:
                original_repos += 1
            
            if repo.get('language'):
                languages[repo['language']] += 1
            
            total_stars += repo.get('stargazers_count', 0)
        
        # Get recent activity (commits in last year)
        total_commits = 0
        for repo in repos[:10]:  # Only check top 10 repos
            try:
                commits_response = requests.get(
                    f"https://api.github.com/repos/{username}/{repo['name']}/commits?per_page=100",
                    headers=headers,
                    timeout=5
                )
                if commits_response.status_code == 200:
                    commits = commits_response.json()
                    # Count commits by this user
                    user_commits = [c for c in commits if c.get('author') and c['author'].get('login') == username]
                    total_commits += len(user_commits)
            except:
                continue
        
        return {
            'profile': {
                'username': username,
                'name': user.get('name'),
                'public_repos': user.get('public_repos', 0),
                'followers': user.get('followers', 0),
                'created_at': user.get('created_at'),
                'bio': user.get('bio')
            },
            'repositories': {
                'total': len(repos),
                'original': original_repos,
                'forked': forked_repos,
                'languages': dict(languages),
                'stars_received': total_stars
            },
            'activity': {
                'total_commits': total_commits,
                'account_created_year': datetime.fromisoformat(user['created_at'].replace('Z', '+00:00')).year if user.get('created_at') else None
            }
        }
    
    except Exception as e:
        return {'error': str(e)}
