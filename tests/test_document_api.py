"""Integration test for document processing API"""

import os
import sys
from io import BytesIO

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api import create_app


def test_document_api():
    """Test document processing API endpoints"""
    print("\n=== Testing Document Processing API ===\n")
    
    # Create test app
    app = create_app('testing')
    client = app.test_client()
    
    # Test 1: Health check
    print("1. Testing health check endpoint...")
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    print("   ✅ Health check passed")
    
    # Test 2: Validate endpoint with no file
    print("\n2. Testing validation endpoint with no file...")
    response = client.post('/api/documents/validate')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    print(f"   ✅ Correctly rejected: {data['error']}")
    
    # Test 3: Validate endpoint with valid file
    print("\n3. Testing validation endpoint with valid PDF...")
    data = {
        'file': (BytesIO(b'%PDF-1.4 fake pdf content'), 'test.pdf')
    }
    response = client.post('/api/documents/validate', data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    result = response.get_json()
    assert result['valid'] == True
    assert result['extension'] == 'pdf'
    print(f"   ✅ Validation passed: {result['filename']}")
    
    # Test 4: Validate endpoint with invalid extension
    print("\n4. Testing validation endpoint with invalid extension...")
    data = {
        'file': (BytesIO(b'test content'), 'test.doc')
    }
    response = client.post('/api/documents/validate', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    result = response.get_json()
    assert result['valid'] == False
    print(f"   ✅ Correctly rejected: {result['error']}")
    
    # Test 5: Upload endpoint with no file
    print("\n5. Testing upload endpoint with no file...")
    response = client.post('/api/documents/upload')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    print(f"   ✅ Correctly rejected: {data['error']}")
    
    # Test 6: Upload endpoint with invalid document type
    print("\n6. Testing upload endpoint with invalid document type...")
    data = {
        'file': (BytesIO(b'%PDF-1.4 fake pdf'), 'test.pdf'),
        'document_type': 'invalid'
    }
    response = client.post('/api/documents/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    result = response.get_json()
    assert 'error' in result
    print(f"   ✅ Correctly rejected: {result['error']}")
    
    # Test 7: Upload endpoint with valid request (will fail without OpenAI key)
    print("\n7. Testing upload endpoint with valid request...")
    data = {
        'file': (BytesIO(b'%PDF-1.4 fake pdf content'), 'resume.pdf'),
        'document_type': 'cv'
    }
    response = client.post('/api/documents/upload', data=data, content_type='multipart/form-data')
    
    if os.getenv('OPENAI_API_KEY'):
        print("   ⚠️  OpenAI API key found - would process document")
    else:
        print("   ⚠️  OpenAI API key not found - expected to fail")
        assert response.status_code in [400, 500]
    
    result = response.get_json()
    print(f"   Response: {result.get('error', 'Success')}")
    
    print("\n✅ All API endpoint tests passed!")


def test_blueprints_registered():
    """Test that all blueprints are registered"""
    print("\n=== Testing Blueprint Registration ===\n")
    
    app = create_app('testing')
    
    # Get all registered blueprints
    blueprints = list(app.blueprints.keys())
    print(f"Registered blueprints: {blueprints}")
    
    # Check for required blueprints
    assert 'verifications' in blueprints, "Verifications blueprint not registered"
    assert 'documents' in blueprints, "Documents blueprint not registered"
    
    print("✅ All required blueprints registered")


def test_routes_available():
    """Test that all routes are available"""
    print("\n=== Testing Route Availability ===\n")
    
    app = create_app('testing')
    
    # Get all routes
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'path': str(rule)
        })
    
    # Print all routes
    print("Available routes:")
    for route in routes:
        if route['endpoint'] not in ['static']:
            methods = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
            print(f"   {methods:20} {route['path']}")
    
    # Check for required routes
    paths = [r['path'] for r in routes]
    assert '/health' in paths
    assert '/api/documents/upload' in paths
    assert '/api/documents/validate' in paths
    
    print("\n✅ All required routes available")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Document Processing API Integration Tests")
    print("=" * 60)
    
    try:
        test_blueprints_registered()
        test_routes_available()
        test_document_api()
        
        print("\n" + "=" * 60)
        print("All Tests Passed! ✅")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
