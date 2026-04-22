#!/usr/bin/env python3
"""
Test script for Sentence API endpoints
Run this after starting the backend server with: python run.py
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_sentence_api():
    print("🧪 Testing Sentence API Endpoints")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL.replace('/api', '')}/")
        print(f"✅ Server Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running!")
        print("   Please start the server with: python run.py")
        return
    except Exception as e:
        print(f"❌ Server error: {e}")
        return
    
    print()
    
    # Test 2: Test sentence creation endpoint (without auth - should fail)
    print("🔒 Testing POST /api/sentences (without auth - should fail)")
    try:
        data = {
            "pattern_id": 1,
            "term": "Hello world",
            "definition": "Xin chào thế giới",
            "status": "unknown"
        }
        response = requests.post(f"{BASE_URL}/sentences", json=data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Auth protection working correctly")
        else:
            print("⚠️  Expected 401 Unauthorized")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 3: Test sentence list endpoint (without auth - should fail)
    print("🔒 Testing GET /api/sentences?pattern_id=1 (without auth - should fail)")
    try:
        response = requests.get(f"{BASE_URL}/sentences?pattern_id=1")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 401:
            print("✅ Auth protection working correctly")
        else:
            print("⚠️  Expected 401 Unauthorized")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    
    # Test 4: Check API structure
    print("📋 API Endpoint Structure:")
    print("   POST   /api/sentences              - Create sentence")
    print("   GET    /api/sentences?pattern_id=X - List sentences")
    print("   GET    /api/sentences/{id}         - Get sentence")
    print("   PUT    /api/sentences/{id}         - Update sentence")
    print("   DELETE /api/sentences/{id}         - Delete sentence")
    print("   GET    /api/sentences/recent       - Recent sentences")
    
    print()
    print("🔑 Required Headers:")
    print("   Authorization: Bearer <firebase_token>")
    print("   Content-Type: application/json")
    
    print()
    print("📝 Create Sentence Request Body:")
    print(json.dumps({
        "pattern_id": 1,
        "term": "Where is the nearest station?",
        "definition": "Ga gần nhất ở đâu?",
        "status": "unknown",
        "mistakes": 0
    }, indent=2))
    
    print()
    print("📝 Update Sentence Request Body:")
    print(json.dumps({
        "term": "Where is the nearest station?",
        "definition": "Ga gần nhất ở đâu?",
        "status": "known",
        "mistakes": 1
    }, indent=2))

if __name__ == "__main__":
    test_sentence_api()