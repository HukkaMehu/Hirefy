"""
Simple validation test for backend structure and files
Run from backend/ directory: python validate_structure.py
"""
import os
import json
from pathlib import Path

def validate_structure():
    """Validate directory structure exists"""
    print("=== Validating Directory Structure ===")
    
    required_dirs = [
        "services",
        "mocks"
    ]
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"[OK] {dir_name}/ directory exists")
        else:
            print(f"[FAIL] {dir_name}/ directory missing")
            return False
    
    return True

def validate_files():
    """Validate required files exist"""
    print("\n=== Validating Files ===")
    
    required_files = {
        "services/github_api.py": "GitHub API client",
        "services/mock_loader.py": "Mock data loader",
        "services/__init__.py": "Services package init",
        "mocks/reference_templates.json": "Reference templates",
        "mocks/fraud_scenarios.json": "Fraud scenarios",
        "config.py": "Configuration",
        "__init__.py": "Backend package init"
    }
    
    all_exist = True
    for file_path, description in required_files.items():
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"[OK] {file_path:40s} ({size:,} bytes) - {description}")
        else:
            print(f"[FAIL] {file_path:40s} - {description} MISSING")
            all_exist = False
    
    return all_exist

def validate_json_files():
    """Validate JSON files are valid"""
    print("\n=== Validating JSON Files ===")
    
    json_files = [
        "mocks/reference_templates.json",
        "mocks/fraud_scenarios.json"
    ]
    
    all_valid = True
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            print(f"[OK] {json_file:40s} - Valid JSON ({len(json.dumps(data))} chars)")
            
            # Additional validation
            if "reference_templates" in json_file:
                templates = data.get("templates", [])
                print(f"     Contains {len(templates)} reference templates")
                total_weight = sum(t.get("weight", 0) for t in templates)
                print(f"     Total weight: {total_weight:.1f}")
                
            if "fraud_scenarios" in json_file:
                scenarios = data.get("scenarios", [])
                print(f"     Contains {len(scenarios)} fraud scenarios")
                red_flags = sum(1 for s in scenarios if s.get("severity") == "red")
                yellow_flags = sum(1 for s in scenarios if s.get("severity") == "yellow")
                print(f"     Red flags: {red_flags}, Yellow flags: {yellow_flags}")
                
        except json.JSONDecodeError as e:
            print(f"[FAIL] {json_file:40s} - Invalid JSON: {e}")
            all_valid = False
        except Exception as e:
            print(f"[FAIL] {json_file:40s} - Error: {e}")
            all_valid = False
    
    return all_valid

def validate_python_syntax():
    """Validate Python files have valid syntax"""
    print("\n=== Validating Python Syntax ===")
    
    python_files = [
        "services/github_api.py",
        "services/mock_loader.py"
    ]
    
    all_valid = True
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, py_file, 'exec')
            print(f"[OK] {py_file:40s} - Valid Python syntax")
        except SyntaxError as e:
            print(f"[FAIL] {py_file:40s} - Syntax Error: {e}")
            all_valid = False
        except Exception as e:
            print(f"[FAIL] {py_file:40s} - Error: {e}")
            all_valid = False
    
    return all_valid

def check_dependencies():
    """Check if required dependencies are in requirements.txt"""
    print("\n=== Checking Dependencies ===")
    
    required_deps = ["requests", "faker", "pydantic-settings"]
    
    with open("requirements.txt", 'r') as f:
        requirements = f.read()
    
    for dep in required_deps:
        if dep in requirements.lower():
            print(f"[OK] {dep} found in requirements.txt")
        else:
            print(f"[WARN] {dep} not found in requirements.txt")

if __name__ == "__main__":
    print("=" * 60)
    print("Backend Structure Validation")
    print("=" * 60)
    print()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    results = []
    results.append(validate_structure())
    results.append(validate_files())
    results.append(validate_json_files())
    results.append(validate_python_syntax())
    check_dependencies()
    
    print("\n" + "=" * 60)
    if all(results):
        print("SUCCESS: All validation checks passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up .env file with GITHUB_TOKEN")
        print("3. Run: python test_services.py")
    else:
        print("FAILED: Some validation checks failed")
        print("=" * 60)
