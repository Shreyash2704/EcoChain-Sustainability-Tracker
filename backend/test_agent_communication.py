#!/usr/bin/env python3
"""
Test script for agent communication flow
"""

import requests
import json
import tempfile
import os

def test_agent_communication():
    """Test the verifier → reasoner agent communication"""
    print("🧪 Testing Agent Communication Flow")
    print("=" * 50)
    
    # Create a test sustainability document
    test_data = {
        "sustainability_metrics": {
            "carbon_footprint": 200.0,
            "energy_consumption": 3000,
            "waste_reduction": 20.0,
            "renewable_energy_percentage": 90.0
        },
        "company_info": {
            "name": "GreenTech Solutions",
            "industry": "Technology",
            "location": "San Francisco, CA"
        },
        "verification_date": "2024-01-15",
        "certification_body": "Green Standards Inc."
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, indent=2)
        temp_file_path = f.name
    
    try:
        print("📤 Uploading test document...")
        
        # Upload file
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('sustainability_report.json', f, 'application/json')}
            data = {
                'upload_type': 'sustainability_document',
                'user_wallet': '0x1234567890abcdef1234567890abcdef12345678',
                'metadata': json.dumps({'description': 'Test agent communication'})
            }
            
            response = requests.post('http://localhost:8002/upload/', files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Upload successful!")
                print(f"📊 Upload ID: {result['upload_id']}")
                print(f"🔗 CID: {result['cid']}")
                print(f"📄 Status: {result['status']}")
                print(f"💬 Message: {result['message']}")
                
                print("\n🎯 Expected Agent Flow:")
                print("1. ✅ Verifier Agent: Processed file and generated CID")
                print("2. 📤 Verifier → Reasoner: Sent document data for analysis")
                print("3. 🧠 Reasoner Agent: Analyzing document with MeTTa service")
                print("4. 🎯 Reasoner: Calculating carbon credits")
                print("5. 📊 Reasoner: Displaying analysis results in terminal")
                print("6. 📤 Reasoner → Verifier: Sending analysis results back")
                
                print(f"\n🔍 Check the server terminal for detailed agent communication logs!")
                print(f"   Look for messages starting with:")
                print(f"   - 📤 Sent data to reasoner agent")
                print(f"   - 🧠 REASONING ANALYSIS STARTED")
                print(f"   - 🎯 CARBON CREDIT ANALYSIS")
                print(f"   - 📤 Analysis results sent back")
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Error: {response.text}")
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
    
    finally:
        # Clean up
        try:
            os.unlink(temp_file_path)
            print(f"\n🗑️ Cleaned up test file")
        except:
            pass

if __name__ == "__main__":
    print("🚀 Agent Communication Test")
    print("Make sure the server is running on http://localhost:8002")
    print("=" * 60)
    test_agent_communication()
    print("=" * 60)
    print("🏁 Test completed!")
    print("\n💡 Next steps:")
    print("1. Check server terminal for agent communication logs")
    print("2. Verify reasoner agent analysis output")
    print("3. Test with different document types")
