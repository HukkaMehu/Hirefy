"""
API routes for AI data compilation and analysis
"""
from flask import Blueprint, jsonify, request, send_file
from src.core.ai_data_compiler import AIDataCompiler
from src.core.ai_analyzer import AIAnalyzer
import tempfile
import json

ai_analysis_bp = Blueprint('ai_analysis', __name__)
ai_analyzer = AIAnalyzer()


@ai_analysis_bp.route('/verifications/<int:verification_id>/compile', methods=['GET'])
def compile_verification_data(verification_id):
    """Compile all data for a verification"""
    try:
        compiler = AIDataCompiler()
        compiled_data = compiler.compile_verification_data(verification_id)
        
        return jsonify({
            "success": True,
            "data": compiled_data
        })
    
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_analysis_bp.route('/verifications/<int:verification_id>/ai-prompt', methods=['GET'])
def get_ai_analysis_prompt(verification_id):
    """Get AI analysis prompt with all compiled data"""
    try:
        compiler = AIDataCompiler()
        ai_prompt = compiler.export_for_ai_analysis(verification_id)
        
        return jsonify({
            "success": True,
            "prompt": ai_prompt
        })
    
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_analysis_bp.route('/verifications/<int:verification_id>/export', methods=['GET'])
def export_verification_data(verification_id):
    """Export compiled data as downloadable JSON file"""
    try:
        compiler = AIDataCompiler()
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            compiled_data = compiler.compile_verification_data(verification_id)
            ai_prompt = compiler.export_for_ai_analysis(verification_id)
            
            export_data = {
                "compiled_data": compiled_data,
                "ai_analysis_prompt": ai_prompt
            }
            
            json.dump(export_data, f, indent=2, ensure_ascii=False)
            temp_path = f.name
        
        return send_file(
            temp_path,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'verification_{verification_id}_ai_data.json'
        )
    
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_analysis_bp.route('/verifications/compile-all', methods=['GET'])
def compile_all_verifications():
    """Compile data for all verifications"""
    try:
        compiler = AIDataCompiler()
        all_data = compiler.compile_all_verifications()
        
        return jsonify({
            "success": True,
            "count": len(all_data),
            "data": all_data
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_analysis_bp.route('/verifications/<verification_id>/analyze', methods=['POST'])
def analyze_verification(verification_id):
    """Run AI analysis on a verification"""
    try:
        # Get optional model parameter
        data = request.get_json() or {}
        model = data.get('model', 'gpt-4o')
        
        # Run analysis
        result = ai_analyzer.analyze_verification(verification_id, model=model)
        
        if not result['success']:
            return jsonify(result), 500
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@ai_analysis_bp.route('/verifications/<verification_id>/quick-summary', methods=['POST'])
def quick_summary(verification_id):
    """Generate a quick summary using faster model"""
    try:
        result = ai_analyzer.quick_summary(verification_id)
        
        if not result['success']:
            return jsonify(result), 500
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
