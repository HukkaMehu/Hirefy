import json
import random
from pathlib import Path
from functools import lru_cache
from faker import Faker

MOCKS_DIR = Path(__file__).parent.parent / "mocks"
fake = Faker()

@lru_cache()
def load_reference_templates() -> dict:
    with open(MOCKS_DIR / "reference_templates.json") as f:
        return json.load(f)

@lru_cache()
def load_fraud_scenarios() -> dict:
    with open(MOCKS_DIR / "fraud_scenarios.json") as f:
        return json.load(f)

def get_weighted_reference_response() -> dict:
    """Get random reference response using weighted distribution"""
    templates = load_reference_templates()["templates"]
    weights = [t["weight"] for t in templates]
    selected = random.choices(templates, weights=weights)[0]
    
    return {
        "performance_rating": selected["performance_rating"],
        "strengths": selected["strengths"].copy(),
        "weaknesses": selected["weaknesses"].copy(),
        "would_rehire": selected["would_rehire"],
        "specific_example": random.choice(selected["examples"])
    }

def generate_mock_references(employment_history: list) -> list:
    """Generate 50-100 realistic mock former coworkers"""
    all_references = []
    
    for job in employment_history:
        company = job["company"]
        num_coworkers = random.randint(15, 25)
        
        for _ in range(num_coworkers):
            ref = {
                "id": fake.uuid4(),
                "name": fake.name(),
                "company": company,
                "title": random.choice([
                    "Engineering Manager",
                    "Senior Developer",
                    "Tech Lead",
                    "Product Manager",
                    "Software Engineer"
                ]),
                "relationship": random.choice(["Manager", "Peer", "Peer", "Direct Report"])
            }
            all_references.append(ref)
    
    return all_references

def simulate_outreach_responses(references: list, response_rate: float = 0.20) -> list:
    """Simulate 20% response rate with mock answers"""
    num_responses = int(len(references) * response_rate)
    responding_refs = random.sample(references, min(num_responses, len(references)))
    
    responses = []
    for ref in responding_refs:
        response = get_weighted_reference_response()
        response.update({
            "reference_id": ref["id"],
            "reference_name": ref["name"],
            "reference_title": ref["title"],
            "company": ref["company"],
            "relationship": ref["relationship"]
        })
        responses.append(response)
    
    return responses
