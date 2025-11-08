from typing import Literal
from dataclasses import dataclass, asdict
from datetime import datetime
from config import get_settings

settings = get_settings()

FraudLevel = Literal["green", "yellow", "red"]

@dataclass
class FraudFlag:
    type: str
    severity: str  # "low" | "medium" | "high" | "critical"
    message: str
    category: str
    evidence: dict

class FraudDetector:
    """Modular fraud detection engine"""
    
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.rules = [
            self._check_github_consistency,
            self._check_employment_timeline,
            self._check_reference_sentiment,
            self._check_job_title_consistency,
            self._check_company_existence,
            self._check_social_media_presence,
        ]
    
    def analyze(
        self,
        resume_data: dict,
        github_data: dict = None,
        reference_responses: list = None,
    ) -> dict:
        """Run all fraud detection rules"""
        
        all_flags = []
        
        # Run each rule
        for rule in self.rules:
            try:
                flags = rule(resume_data, github_data or {}, reference_responses or [])
                all_flags.extend(flags)
            except Exception as e:
                print(f"Rule error: {e}")
                continue
        
        # Calculate risk
        risk_level = self._calculate_risk_level(all_flags)
        
        return {
            "risk_level": risk_level,
            "flags": [asdict(f) for f in all_flags],
            "flag_count": {
                "critical": len([f for f in all_flags if f.severity == "critical"]),
                "high": len([f for f in all_flags if f.severity == "high"]),
                "medium": len([f for f in all_flags if f.severity == "medium"]),
                "low": len([f for f in all_flags if f.severity == "low"])
            },
            "summary": self._generate_summary(risk_level, all_flags)
        }
    
    def _check_github_consistency(self, resume, github, refs) -> list:
        """Check if resume skills match GitHub languages"""
        flags = []
        
        if not github or "error" in github:
            return flags
        
        resume_skills = [s.lower() for s in resume.get("skills", [])]
        github_langs = [lang.lower() for lang in github.get("repositories", {}).get("languages", {}).keys()]
        
        # Map frameworks to languages
        skill_map = settings.skill_map
        
        for skill in settings.skills_to_check:
            if skill in resume_skills:
                mapped = skill_map.get(skill, skill)
                
                if mapped not in github_langs and skill not in github_langs:
                    flags.append(FraudFlag(
                        type="skill_mismatch",
                        severity="high",
                        message=f"Resume claims {skill.title()} expertise, but GitHub shows 0 {skill.title()} code",
                        category="Technical Skills",
                        evidence={"claimed": skill, "github_languages": github_langs}
                    ))
        
        return flags
    
    def _check_employment_timeline(self, resume, github, refs) -> list:
        """Detect employment gaps > 6 months"""
        flags = []
        
        jobs = sorted(resume.get("employment_history", []), key=lambda j: j.get("start_date", ""))
        
        for i in range(len(jobs) - 1):
            gap_months = self._calculate_gap_months(jobs[i].get("end_date", ""), jobs[i+1].get("start_date", ""))
            
            if gap_months > settings.employment_gap_threshold:
                flags.append(FraudFlag(
                    type="employment_gap",
                    severity="medium",
                    message=f"{gap_months}-month gap between {jobs[i].get('company')} and {jobs[i+1].get('company')}",
                    category="Employment History",
                    evidence={
                        "gap_start": jobs[i].get("end_date"),
                        "gap_end": jobs[i+1].get("start_date"),
                        "gap_months": gap_months
                    }
                ))
        
        return flags
    
    def _check_reference_sentiment(self, resume, github, refs) -> list:
        """Flag negative reference patterns"""
        flags = []
        
        if not refs:
            return flags
        
        avg_rating = sum(r.get("performance_rating", 7) for r in refs) / len(refs)
        would_not_rehire = [r for r in refs if not r.get("would_rehire", True)]
        
        if avg_rating < settings.avg_rating_threshold:
            flags.append(FraudFlag(
                type="low_performance_ratings",
                severity="high",
                message=f"Average reference rating {avg_rating:.1f}/10 (below threshold)",
                category="References",
                evidence={"avg_rating": avg_rating, "total_references": len(refs)}
            ))
        
        if len(would_not_rehire) >= settings.rehire_concern_threshold:
            flags.append(FraudFlag(
                type="rehire_concerns",
                severity="high",
                message=f"{len(would_not_rehire)} of {len(refs)} references would NOT rehire",
                category="References",
                evidence={"would_not_rehire_count": len(would_not_rehire)}
            ))
        
        return flags

    def _check_job_title_consistency(self, resume, github, refs) -> list:
        """Check for inflated or inconsistent job titles"""
        flags = []
        
        unprofessional_titles = ["ninja", "guru", "rockstar", "wizard"]
        
        for job in resume.get("employment_history", []):
            title = job.get("title", "").lower()
            if any(unprofessional in title for unprofessional in unprofessional_titles):
                flags.append(FraudFlag(
                    type="unprofessional_job_title",
                    severity="low",
                    message=f"Unprofessional job title: '{job.get('title')}'",
                    category="Employment History",
                    evidence={"job_title": job.get('title')}
                ))
        
        return flags

    def _check_company_existence(self, resume, github, refs) -> list:
        """Check if companies listed in the resume have a web presence"""
        flags = []
        
        # This is a mock implementation. In a real implementation, we would
        # use a more reliable method to check for company existence.
        import requests
        
        for job in resume.get("employment_history", []):
            company_name = job.get("company", "")
            if company_name:
                try:
                    # A very basic check to see if a website exists for the company
                    response = requests.get(f"https://{company_name.replace(' ', '').lower()}.com", timeout=5)
                    if response.status_code != 200:
                        flags.append(FraudFlag(
                            type="company_not_found",
                            severity="medium",
                            message=f"Could not verify existence of company: {company_name}",
                            category="Employment History",
                            evidence={"company_name": company_name}
                        ))
                except requests.exceptions.RequestException:
                    flags.append(FraudFlag(
                        type="company_not_found",
                        severity="medium",
                        message=f"Could not verify existence of company: {company_name}",
                        category="Employment History",
                        evidence={"company_name": company_name}
                    ))

        return flags

    def _check_social_media_presence(self, resume, github, refs) -> list:
        """Check for a LinkedIn profile and consistency"""
        flags = []
        
        linkedin_url = resume.get("linkedin_url")
        
        if not linkedin_url:
            flags.append(FraudFlag(
                type="no_linkedin_profile",
                severity="low",
                message="No LinkedIn profile provided",
                category="Social Media",
                evidence={}
            ))
        else:
            # This is a mock implementation. In a real implementation, we would
            # use a web scraping service to get the LinkedIn profile data.
            import requests
            try:
                response = requests.get(linkedin_url, timeout=5)
                if response.status_code != 200:
                    flags.append(FraudFlag(
                        type="linkedin_profile_not_found",
                        severity="medium",
                        message=f"LinkedIn profile not found at: {linkedin_url}",
                        category="Social Media",
                        evidence={"linkedin_url": linkedin_url}
                    ))
            except requests.exceptions.RequestException:
                flags.append(FraudFlag(
                    type="linkedin_profile_not_found",
                    severity="medium",
                    message=f"LinkedIn profile not found at: {linkedin_url}",
                    category="Social Media",
                    evidence={"linkedin_url": linkedin_url}
                ))

        return flags
    
    def _calculate_risk_level(self, flags: list) -> FraudLevel:
        """Determine overall risk"""
        if any(f.severity == "critical" for f in flags):
            return "red"
        
        high_count = len([f for f in flags if f.severity == "high"])
        if high_count >= 2:
            return "red"
        
        medium_count = len([f for f in flags if f.severity == "medium"])
        if high_count >= 1 or medium_count >= 3:
            return "yellow"
        
        return "green"
    
    def _generate_summary(self, risk_level: FraudLevel, flags: list) -> str:
        if risk_level == "green":
            return "Verification successful. All claims verified with no major concerns."
        
        critical_msgs = [f.message for f in flags if f.severity in ["critical", "high"]]
        
        if risk_level == "red":
            return f"CRITICAL ISSUES: {'; '.join(critical_msgs[:2])}"
        else:
            return f"Minor concerns detected: {'; '.join(critical_msgs[:2])}"
    
    def _calculate_gap_months(self, end_date: str, start_date: str) -> int:
        """Calculate months between two YYYY-MM dates"""
        try:
            end = datetime.strptime(end_date, "%Y-%m")
            start = datetime.strptime(start_date, "%Y-%m")
            return (start.year - end.year) * 12 + (start.month - end.month)
        except:
            return 0
