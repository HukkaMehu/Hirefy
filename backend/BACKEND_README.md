# Backend Services - GitHub API & Mock Data System

## Overview
This directory contains the GitHub API client and mock data system for the CV verification platform.

## Structure
```
backend/
├── services/
│   ├── github_api.py       # Real GitHub REST API client
│   └── mock_loader.py      # Mock data generation system
├── mocks/
│   ├── reference_templates.json    # Reference response templates
│   └── fraud_scenarios.json        # Fraud detection scenarios
├── config.py               # Application configuration
├── test_services.py        # Test suite
└── validate_structure.py   # Structure validator
```

## Key Components

### 1. GitHub API Client (`services/github_api.py`)
- **Function**: `analyze_github_profile(username: str) -> dict`
- Fetches real data from GitHub REST API
- Returns profile, repositories, languages, commits, and activity
- Handles rate limiting and errors gracefully
- Uses optional GitHub token from environment

**Example Usage:**
```python
from services.github_api import analyze_github_profile

result = analyze_github_profile('torvalds')
print(result['profile']['name'])  # Linus Torvalds
print(result['repositories']['languages'])  # {'C': 25, 'Shell': 3, ...}
print(result['activity']['total_commits'])  # 1234
```

### 2. Mock Data Loader (`services/mock_loader.py`)
Generates realistic mock data for testing and demos.

**Functions:**
- `get_weighted_reference_response()` - Returns weighted random reference (60% positive, 30% neutral, 10% negative)
- `generate_mock_references(employment_history)` - Creates 50-100 mock former coworkers
- `simulate_outreach_responses(references, response_rate=0.20)` - Simulates 20% response rate

**Example Usage:**
```python
from services.mock_loader import generate_mock_references, simulate_outreach_responses

employment = [{"company": "TechCorp"}, {"company": "StartupX"}]
references = generate_mock_references(employment)  # ~40-50 references
responses = simulate_outreach_responses(references)  # ~8-10 responses
```

### 3. Reference Templates (`mocks/reference_templates.json`)
Contains 3 weighted templates:
- **Strong Performer** (60% weight): Rating 8/10, would rehire
- **Solid Contributor** (30% weight): Rating 7/10, would rehire
- **Performance Concerns** (10% weight): Rating 5/10, would not rehire

### 4. Fraud Scenarios (`mocks/fraud_scenarios.json`)
Contains 5 common fraud patterns:
- **Red Flags** (3): Fake GitHub activity, title inflation, fake education
- **Yellow Flags** (2): Skill exaggeration, employment gaps

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file in project root:
```env
GITHUB_TOKEN=your_github_token_here  # Optional but recommended for higher rate limits
```

### 3. Validate Installation
```bash
python validate_structure.py
```

### 4. Run Tests
```bash
python test_services.py
```

## Testing

### Validation Test (No dependencies required)
```bash
python validate_structure.py
```
Checks:
- Directory structure
- File existence and sizes
- JSON validity
- Python syntax
- Dependencies in requirements.txt

### Full Test Suite (Requires dependencies)
```bash
python test_services.py
```
Tests:
- GitHub API client (real API call to GitHub)
- Mock data generation
- Weighted reference responses
- Outreach simulation
- Fraud scenarios loading

### Manual Testing

**GitHub API:**
```bash
python -c "from services.github_api import analyze_github_profile; import json; print(json.dumps(analyze_github_profile('torvalds'), indent=2))"
```

**Mock Data:**
```bash
python -c "from services.mock_loader import get_weighted_reference_response; import json; print(json.dumps(get_weighted_reference_response(), indent=2))"
```

**Reference Generation:**
```bash
python -c "from services.mock_loader import generate_mock_references; refs = generate_mock_references([{'company': 'TestCorp'}]); print(f'Generated {len(refs)} references')"
```

## API Response Formats

### GitHub Profile Analysis
```json
{
  "profile": {
    "username": "torvalds",
    "name": "Linus Torvalds",
    "public_repos": 25,
    "followers": 180000,
    "created_at": "2011-09-03T15:26:22Z",
    "bio": "Creator of Linux and Git"
  },
  "repositories": {
    "total": 25,
    "original": 20,
    "forked": 5,
    "languages": {"C": 18, "Shell": 3, "Python": 2},
    "stars_received": 150000
  },
  "activity": {
    "total_commits": 1234,
    "account_created_year": 2011
  }
}
```

### Mock Reference Response
```json
{
  "performance_rating": 8,
  "strengths": ["Strong technical skills", "Excellent collaborator"],
  "weaknesses": ["Sometimes misses deadlines under pressure"],
  "would_rehire": true,
  "specific_example": "Led the payment infrastructure rebuild, delivered 3 weeks early",
  "reference_id": "uuid-here",
  "reference_name": "John Smith",
  "reference_title": "Engineering Manager",
  "company": "TechCorp",
  "relationship": "Manager"
}
```

## Error Handling

### GitHub API Errors
- **404 Not Found**: Returns `{"error": "GitHub user not found"}`
- **Rate Limit**: Caught by exception handler
- **Timeout**: 10 second timeout for profile, 5 seconds per repo
- **Network Error**: Returns `{"error": "error message"}`

### Mock Data Errors
- File not found: Handled by lru_cache
- Invalid JSON: Raises exception at startup
- Empty employment history: Returns empty list

## Performance Notes

### GitHub API
- Profile fetch: ~200-500ms
- Repository list: ~300-800ms
- Commit analysis: ~2-5 seconds (10 repos × 100 commits)
- **Total**: ~3-6 seconds per profile

### Mock Data
- Reference generation: <10ms for 100 references
- Weighted selection: <1ms per call
- Outreach simulation: <5ms for 100 references

## Rate Limits

### GitHub API
- **Unauthenticated**: 60 requests/hour
- **Authenticated**: 5,000 requests/hour
- **Recommendation**: Use `GITHUB_TOKEN` in production

### Mock Data
- No rate limits (local generation)
- Uses Python `random` module for distribution

## Dependencies
```
requests==2.31.0          # HTTP client for GitHub API
faker==20.1.0             # Generate realistic mock data
pydantic-settings==2.1.0  # Configuration management
```

## Future Enhancements
- [ ] Add caching layer for GitHub API responses
- [ ] Implement GraphQL API for faster data fetching
- [ ] Add more fraud scenario templates
- [ ] Create reference response variations
- [ ] Add LinkedIn API integration (when available)
- [ ] Implement mock employment verification
- [ ] Add education verification mock data
