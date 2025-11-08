"""
Simple transcript API - just show the raw transcripts
"""
from flask import Blueprint, jsonify
import os
from pathlib import Path

transcripts_bp = Blueprint('transcripts', __name__)


@transcripts_bp.route('/verifications/<session_id>/transcripts', methods=['GET'])
def get_transcripts(session_id):
    """Get all transcripts for a verification session"""
    
    # Get candidate name from database
    from src.database.models import VerificationSession
    session = VerificationSession.query.get(session_id)
    
    if not session:
        return jsonify({'error': 'Verification not found'}), 404
    
    candidate_name = session.candidate.full_name
    
    # Normalize candidate name (same as TranscriptManager does)
    normalized_name = candidate_name.strip().lower().replace(" ", "_")
    
    # Look for transcript folder
    transcript_dir = Path('transcripts') / normalized_name
    
    if not transcript_dir.exists():
        return jsonify({
            'success': True,
            'transcripts': [],
            'message': 'No transcripts found yet'
        })
    
    # Read all transcript files
    transcripts = []
    for file in transcript_dir.glob('*.txt'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                transcripts.append({
                    'filename': file.name,
                    'content': content,
                    'timestamp': file.stat().st_mtime
                })
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Sort by timestamp
    transcripts.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return jsonify({
        'success': True,
        'transcripts': transcripts,
        'count': len(transcripts)
    })


@transcripts_bp.route('/verifications/<session_id>/ai-summary', methods=['POST'])
def generate_ai_summary(session_id):
    """Generate AI summary from transcripts"""
    
    # Get candidate name from database
    from src.database.models import VerificationSession
    session = VerificationSession.query.get(session_id)
    
    if not session:
        return jsonify({'error': 'Verification not found'}), 404
    
    candidate_name = session.candidate.full_name
    
    # Normalize candidate name (same as TranscriptManager does)
    normalized_name = candidate_name.strip().lower().replace(" ", "_")
    
    # Look for transcript folder
    transcript_dir = Path('transcripts') / normalized_name
    
    if not transcript_dir.exists():
        return jsonify({
            'success': False,
            'error': 'No transcripts found'
        }), 404
    
    # Read all transcript files
    all_transcripts = []
    for file in transcript_dir.glob('*.txt'):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                all_transcripts.append(f.read())
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    if not all_transcripts:
        return jsonify({
            'success': False,
            'error': 'No transcripts found'
        }), 404
    
    # Combine all transcripts
    combined_transcripts = "\n\n=== NEXT CALL ===\n\n".join(all_transcripts)
    
    # Call OpenAI
    try:
        from openai import OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            return jsonify({
                'success': False,
                'error': 'OpenAI API key not configured'
            }), 500
        
        client = OpenAI(api_key=api_key)
        
        prompt = f"""Analyze these employment verification call transcripts.

TRANSCRIPTS:
{combined_transcripts}

Provide a SUPER CONCISE executive summary (3-4 sentences max).

Start with: "Based on all data analyzed, this candidate..."

Then briefly cover:
- Key verification findings
- Any red flags or concerns
- Final recommendation (HIRE / DO NOT HIRE / NEEDS FURTHER REVIEW)

Be direct and actionable. Reference specific quotes only if critical."""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert employment verification analyst. Be extremely concise and direct. Start with 'Based on all data analyzed, this candidate...'"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        summary = response.choices[0].message.content
        
        return jsonify({
            'success': True,
            'summary': summary,
            'model': 'gpt-4o',
            'tokens': response.usage.total_tokens
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
