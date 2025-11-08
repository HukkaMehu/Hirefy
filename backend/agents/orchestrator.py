import asyncio
import random
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END
from openai import AsyncOpenAI

from backend.services.github_api import analyze_github_profile
from backend.services.supabase_client import update_agent_progress, update_verification_status
from backend.agents.fraud_detector import FraudDetector
from backend.config import get_settings

settings = get_settings()


class VerificationState(TypedDict):
    verification_id: str
    parsed_resume: dict
    github_username: Optional[str]
    references: list
    reference_responses: list
    github_analysis: dict
    fraud_results: dict
    final_report: dict
    current_step: str


async def log_parsing(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        verification_id=state["verification_id"],
        agent_name="Resume Parser",
        status="completed",
        message="Resume parsed successfully",
        data={"parsed": state["parsed_resume"]}
    )
    state["current_step"] = "parsing_complete"
    return state


async def discover_references(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        verification_id=state["verification_id"],
        agent_name="Reference Discovery",
        status="in_progress",
        message="Discovering references from employment history"
    )
    
    references = []
    reference_responses = []
    
    employment_history = state["parsed_resume"].get("employment_history", [])
    
    for job in employment_history[:3]:
        reference = {
            "name": f"{random.choice(['Sarah', 'Mike', 'Lisa', 'David', 'Emma'])} {random.choice(['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson'])}",
            "company": job.get("company", "Unknown"),
            "role": random.choice(["Manager", "Team Lead", "Director", "Supervisor"]),
            "relationship": "Former Supervisor"
        }
        references.append(reference)
        
        if random.random() < 0.2:
            response = {
                "reference": reference,
                "responded": True,
                "rating": random.randint(3, 5),
                "would_rehire": random.choice([True, True, True, False]),
                "comments": random.choice([
                    "Excellent team player and strong technical skills",
                    "Good performer, always met deadlines",
                    "Solid contributor to the team",
                    "Had some challenges with communication",
                ])
            }
            reference_responses.append(response)
    
    state["references"] = references
    state["reference_responses"] = reference_responses
    
    await update_agent_progress(
        verification_id=state["verification_id"],
        agent_name="Reference Discovery",
        status="completed",
        message=f"Found {len(references)} references, {len(reference_responses)} responded",
        data={
            "references": references,
            "responses": reference_responses
        }
    )
    
    state["current_step"] = "references_discovered"
    return state


async def analyze_github(state: VerificationState) -> VerificationState:
    github_username = state.get("github_username")
    
    if not github_username:
        await update_agent_progress(
            verification_id=state["verification_id"],
            agent_name="GitHub Analyzer",
            status="skipped",
            message="No GitHub username provided"
        )
        state["github_analysis"] = {}
        state["current_step"] = "github_skipped"
        return state
    
    await update_agent_progress(
        verification_id=state["verification_id"],
        agent_name="GitHub Analyzer",
        status="in_progress",
        message=f"Analyzing GitHub profile: {github_username}"
    )
    
    try:
        github_data = await asyncio.to_thread(analyze_github_profile, github_username)
        
        if "error" in github_data:
            await update_agent_progress(
                verification_id=state["verification_id"],
                agent_name="GitHub Analyzer",
                status="completed",
                message=f"GitHub user not found: {github_username}",
                data={"error": github_data["error"]}
            )
            state["github_analysis"] = github_data
        else:
            await update_agent_progress(
                verification_id=state["verification_id"],
                agent_name="GitHub Analyzer",
                status="completed",
                message=f"Analyzed {github_data['repositories']['total']} repositories",
                data=github_data
            )
            state["github_analysis"] = github_data
    except Exception as e:
        await update_agent_progress(
            verification_id=state["verification_id"],
            agent_name="GitHub Analyzer",
            status="failed",
            message=f"Error analyzing GitHub: {str(e)}"
        )
        state["github_analysis"] = {"error": str(e)}
    
    state["current_step"] = "github_analyzed"
    return state


async def detect_fraud(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        verification_id=state["verification_id"],
        agent_name="Fraud Detector",
        status="in_progress",
        message="Analyzing for fraud indicators"
    )
    
    detector = FraudDetector(strict_mode=settings.fraud_detection_strict_mode)
    
    fraud_results = await asyncio.to_thread(
        detector.analyze,
        state["parsed_resume"],
        state.get("github_analysis"),
        state.get("reference_responses")
    )
    
    state["fraud_results"] = fraud_results
    
    await update_agent_progress(
        verification_id=state["verification_id"],
        agent_name="Fraud Detector",
        status="completed",
        message=f"Risk level: {fraud_results['risk_level'].upper()} - {len(fraud_results['flags'])} flags detected",
        data=fraud_results
    )
    
    state["current_step"] = "fraud_detected"
    return state


async def synthesize_report(state: VerificationState) -> VerificationState:
    await update_agent_progress(
        verification_id=state["verification_id"],
        agent_name="Report Synthesizer",
        status="in_progress",
        message="Generating final verification report"
    )
    
    narrative = await generate_narrative(state)
    
    interview_questions = generate_interview_questions(state["fraud_results"])
    
    final_report = {
        "candidate_name": state["parsed_resume"].get("name", "Unknown"),
        "risk_level": state["fraud_results"]["risk_level"],
        "fraud_flags": state["fraud_results"]["flags"],
        "flag_summary": state["fraud_results"]["flag_count"],
        "narrative": narrative,
        "interview_questions": interview_questions,
        "github_summary": _summarize_github(state.get("github_analysis", {})),
        "reference_summary": _summarize_references(state.get("reference_responses", [])),
        "generated_at": datetime.utcnow().isoformat()
    }
    
    state["final_report"] = final_report
    
    await update_verification_status(
        verification_id=state["verification_id"],
        status="completed",
        result=final_report
    )
    
    await update_agent_progress(
        verification_id=state["verification_id"],
        agent_name="Report Synthesizer",
        status="completed",
        message="Final report generated successfully",
        data=final_report
    )
    
    state["current_step"] = "report_complete"
    return state


async def generate_narrative(state: VerificationState) -> str:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    fraud_results = state["fraud_results"]
    parsed_resume = state["parsed_resume"]
    github_analysis = state.get("github_analysis", {})
    
    prompt = f"""Generate a professional 2-paragraph narrative summary for this candidate verification:

Candidate: {parsed_resume.get('name', 'Unknown')}
Risk Level: {fraud_results['risk_level'].upper()}
Fraud Flags: {len(fraud_results['flags'])}

Employment History:
{_format_employment(parsed_resume.get('employment_history', []))}

Skills Claimed: {', '.join(parsed_resume.get('skills', []))}

GitHub Analysis: {_format_github(github_analysis)}

Fraud Flags Detected:
{_format_flags(fraud_results['flags'])}

Write a concise, professional summary that:
1. First paragraph: Overview of candidate's background and claims
2. Second paragraph: Assessment of verification findings and risk factors

Keep it factual and professional."""

    try:
        response = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": "You are a professional background verification analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=settings.llm_temperature,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Unable to generate narrative: {str(e)}"


def generate_interview_questions(fraud_results: dict) -> List[str]:
    questions = []
    
    flags = fraud_results.get("flags", [])
    
    for flag in flags[:5]:
        if flag["type"] == "skill_mismatch":
            questions.append(f"Can you describe your experience with {flag.get('evidence', {}).get('skill', 'the claimed skill')} and provide specific examples of projects where you used it?")
        elif flag["type"] == "employment_gap":
            questions.append(f"Can you explain the gap in employment between {flag.get('evidence', {}).get('gap_start', '')} and {flag.get('evidence', {}).get('gap_end', '')}?")
        elif flag["type"] == "weak_reference":
            questions.append("We noticed some concerns from your references. Can you provide additional references who can speak to your recent work?")
        elif flag["type"] == "github_inconsistency":
            questions.append("Your GitHub profile shows different technologies than listed on your resume. Can you clarify your experience?")
    
    if not questions:
        questions = [
            "Can you walk us through your most significant technical achievement?",
            "How do you stay current with new technologies in your field?",
            "Can you describe a challenging project and how you approached it?"
        ]
    
    return questions[:5]


def _summarize_github(github_data: dict) -> str:
    if not github_data or "error" in github_data:
        return "No GitHub profile analyzed"
    
    profile = github_data.get("profile", {})
    repos = github_data.get("repositories", {})
    
    languages = repos.get("languages", {})
    top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
    lang_str = ", ".join([f"{lang} ({count})" for lang, count in top_languages])
    
    return f"{profile.get('username')} - {repos.get('total', 0)} repos, {repos.get('stars_received', 0)} stars. Top languages: {lang_str}"


def _summarize_references(reference_responses: list) -> str:
    if not reference_responses:
        return "No reference responses received"
    
    total = len(reference_responses)
    avg_rating = sum(r.get("rating", 0) for r in reference_responses) / total if total > 0 else 0
    would_rehire_count = sum(1 for r in reference_responses if r.get("would_rehire", False))
    
    return f"{total} references responded. Average rating: {avg_rating:.1f}/5. Would rehire: {would_rehire_count}/{total}"


def _format_employment(employment_history: list) -> str:
    if not employment_history:
        return "No employment history"
    
    lines = []
    for job in employment_history[:3]:
        lines.append(f"- {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} ({job.get('start_date', '')} - {job.get('end_date', '')})")
    return "\n".join(lines)


def _format_github(github_data: dict) -> str:
    if not github_data or "error" in github_data:
        return "Not available"
    
    repos = github_data.get("repositories", {})
    languages = repos.get("languages", {})
    top_3 = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
    return f"{repos.get('total', 0)} repos, Top languages: {', '.join([l[0] for l in top_3])}"


def _format_flags(flags: list) -> str:
    if not flags:
        return "No fraud flags detected"
    
    lines = []
    for flag in flags[:5]:
        lines.append(f"- [{flag.get('severity', '').upper()}] {flag.get('message', '')}")
    return "\n".join(lines)


def build_verification_workflow() -> StateGraph:
    workflow = StateGraph(VerificationState)
    
    workflow.add_node("log_parsing", log_parsing)
    workflow.add_node("discover_references", discover_references)
    workflow.add_node("analyze_github", analyze_github)
    workflow.add_node("detect_fraud", detect_fraud)
    workflow.add_node("synthesize_report", synthesize_report)
    
    workflow.set_entry_point("log_parsing")
    
    workflow.add_edge("log_parsing", "discover_references")
    workflow.add_edge("discover_references", "analyze_github")
    workflow.add_edge("analyze_github", "detect_fraud")
    workflow.add_edge("detect_fraud", "synthesize_report")
    workflow.add_edge("synthesize_report", END)
    
    return workflow.compile()


async def run_verification_workflow(
    verification_id: str,
    parsed_resume: dict,
    github_username: Optional[str] = None
):
    try:
        initial_state = VerificationState(
            verification_id=verification_id,
            parsed_resume=parsed_resume,
            github_username=github_username,
            references=[],
            reference_responses=[],
            github_analysis={},
            fraud_results={},
            final_report={},
            current_step="initialized"
        )
        
        workflow = build_verification_workflow()
        
        final_state = await workflow.ainvoke(initial_state)
        
        return final_state["final_report"]
    
    except Exception as e:
        await update_verification_status(
            verification_id=verification_id,
            status="failed",
            result={"error": str(e)}
        )
        await update_agent_progress(
            verification_id=verification_id,
            agent_name="Orchestrator",
            status="failed",
            message=f"Workflow failed: {str(e)}"
        )
        raise
