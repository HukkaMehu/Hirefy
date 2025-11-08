from supabase import create_client, Client
from config import get_settings

settings = get_settings()
supabase: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_key
)

async def update_agent_progress(
    verification_id: str,
    agent_name: str,
    status: str,
    message: str,
    data: dict = None
):
    """Write progress update to verification_steps table"""
    supabase.table("verification_steps").insert({
        "verification_id": verification_id,
        "agent_name": agent_name,
        "status": status,
        "message": message,
        "data": data
    }).execute()

def get_verification(verification_id: str):
    """Get verification record"""
    result = supabase.table("verifications").select("*").eq("id", verification_id).single().execute()
    return result.data

def update_verification_status(verification_id: str, status: str, result: dict = None):
    """Update verification status and result"""
    update_data = {"status": status}
    if result:
        update_data["result"] = result
    if status == "complete":
        from datetime import datetime
        update_data["completed_at"] = datetime.now().isoformat()
    
    supabase.table("verifications").update(update_data).eq("id", verification_id).execute()
