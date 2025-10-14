"""
Test script for file upload functionality with verifier agent
"""

import requests
import json
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8002"
UPLOAD_URL = f"{BASE_URL}/upload"

def create_test_file():
    """Create a test JSON file for upload"""
    test_data = {
        "sustainability_metrics": {
            "carbon_footprint": 150.5,
            "energy_consumption": 2500,
            "waste_reduction": 15.2,
            "renewable_energy_percentage": 85.0
        },
        "company_info": {
            "name": "Test Company",
            "industry": "Technology",
            "location": "San Francisco, CA"
        },
        "verification_date": "2024-01-15",
        "certification_body": "Green Standards Inc."
    }
    
    test_file_path = Path("test_sustainability_data1.json")
    with open(test_file_path, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    return test_file_path

def test_file_upload():
    """Test the file upload endpoint"""
    print("🧪 Testing file upload with verifier agent...")
    
    # Create test file
    test_file = create_test_file()
    print(f"📄 Created test file: {test_file}")
    
    try:
        # Prepare upload data
        files = {
            'file': (test_file.name, open(test_file, 'rb'), 'application/json')
        }
        
        data = {
            'upload_type': 'sustainability_document',
            'user_wallet': '0x1234567890abcdef1234567890abcdef12345678',
            'metadata': json.dumps({
                'description': 'Test sustainability data upload',
                'category': 'carbon_footprint'
            })
        }
        
        print("📤 Uploading file...")
        response = requests.post(UPLOAD_URL, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            upload_id = result['upload_id']
            print(f"✅ Upload successful! Upload ID: {upload_id}")
            print(f"📊 Response: {json.dumps(result, indent=2)}")
            
            # Test status endpoint
            test_status_endpoint(upload_id)
            
            # Test CID endpoint
            test_cid_endpoint(upload_id)
            
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        # Clean up test file
        if test_file.exists():
            test_file.unlink()
            print(f"🗑️ Cleaned up test file: {test_file}")

def test_status_endpoint(upload_id):
    """Test the status endpoint"""
    print(f"\n📊 Testing status endpoint for upload: {upload_id}")
    
    max_attempts = 10
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{UPLOAD_URL}/{upload_id}/status")
            
            if response.status_code == 200:
                status_data = response.json()
                print(f"📈 Status: {status_data['status']}")
                
                if status_data['status'] == 'completed':
                    print("✅ Upload completed!")
                    if 'cid' in status_data:
                        print(f"🔗 CID: {status_data['cid']}")
                        print(f"🌐 Gateway URL: {status_data['gateway_url']}")
                    break
                else:
                    print(f"⏳ Still processing... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(2)
                    attempt += 1
            else:
                print(f"❌ Status check failed: {response.status_code}")
                break
                
        except Exception as e:
            print(f"❌ Status check error: {str(e)}")
            break
    
    if attempt >= max_attempts:
        print("⏰ Timeout waiting for upload completion")

def test_cid_endpoint(upload_id):
    """Test the CID endpoint"""
    print(f"\n🔗 Testing CID endpoint for upload: {upload_id}")
    
    try:
        response = requests.get(f"{UPLOAD_URL}/{upload_id}/cid")
        
        if response.status_code == 200:
            cid_data = response.json()
            print("✅ CID retrieved successfully!")
            print(f"📊 CID Data: {json.dumps(cid_data, indent=2)}")
        elif response.status_code == 202:
            print("⏳ Upload still processing, CID not yet available")
        else:
            print(f"❌ CID retrieval failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ CID test error: {str(e)}")

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🏥 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check passed!")
            print(f"📊 Health Data: {json.dumps(health_data, indent=2)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting EcoChain Upload Test Suite")
    print("=" * 50)
    
    # Test health endpoint first
    test_health_endpoint()
    
    # Test file upload
    test_file_upload()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
