"""
Test script for Writing Practice API endpoints
Run this to verify all APIs work correctly for the Writing Practice feature
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8002/api"
FIREBASE_TOKEN = "YOUR_FIREBASE_TOKEN_HERE"  # Replace with actual token

# Headers
headers = {
    "Authorization": f"Bearer {FIREBASE_TOKEN}",
    "Content-Type": "application/json"
}

def print_response(title, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print(f"{'='*60}\n")

def test_get_unknown_sentences(pattern_id):
    """Test 1: Get all unknown sentences for a pattern"""
    url = f"{BASE_URL}/sentences"
    params = {
        "pattern_id": pattern_id,
        "status": "unknown",
        "page": 1,
        "page_size": 20
    }
    
    response = requests.get(url, headers=headers, params=params)
    print_response(f"TEST 1: Get Unknown Sentences (pattern_id={pattern_id})", response)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and data.get('data'):
            return data['data'][0]['id']  # Return first sentence ID for next test
    return None

def test_update_sentence_correct(sentence_id):
    """Test 2: Update sentence status to 'known' (correct answer)"""
    url = f"{BASE_URL}/sentences/{sentence_id}"
    
    # First get the sentence details
    get_response = requests.get(url, headers=headers)
    if get_response.status_code != 200:
        print_response(f"TEST 2a: Get Sentence Details (ID={sentence_id})", get_response)
        return
    
    sentence = get_response.json()['data']
    
    # Update to 'known' status
    payload = {
        "term": sentence['term'],
        "definition": sentence['definition'],
        "status": "known",
        "mistakes": sentence['number_of_mistakes']
    }
    
    response = requests.put(url, headers=headers, json=payload)
    print_response(f"TEST 2b: Update Sentence to 'known' (ID={sentence_id})", response)

def test_update_sentence_incorrect(sentence_id):
    """Test 3: Increment mistakes counter (incorrect answer)"""
    url = f"{BASE_URL}/sentences/{sentence_id}"
    
    # First get the sentence details
    get_response = requests.get(url, headers=headers)
    if get_response.status_code != 200:
        print_response(f"TEST 3a: Get Sentence Details (ID={sentence_id})", get_response)
        return
    
    sentence = get_response.json()['data']
    
    # Increment mistakes
    payload = {
        "term": sentence['term'],
        "definition": sentence['definition'],
        "status": "unknown",  # Keep as unknown
        "mistakes": sentence['number_of_mistakes'] + 1
    }
    
    response = requests.put(url, headers=headers, json=payload)
    print_response(f"TEST 3b: Increment Mistakes (ID={sentence_id})", response)

def test_get_all_sentences(pattern_id):
    """Test 4: Get all sentences (both known and unknown)"""
    url = f"{BASE_URL}/sentences"
    params = {
        "pattern_id": pattern_id,
        "page": 1,
        "page_size": 20
    }
    
    response = requests.get(url, headers=headers, params=params)
    print_response(f"TEST 4: Get All Sentences (pattern_id={pattern_id})", response)

def test_get_known_sentences(pattern_id):
    """Test 5: Get only known sentences"""
    url = f"{BASE_URL}/sentences"
    params = {
        "pattern_id": pattern_id,
        "status": "known",
        "page": 1,
        "page_size": 20
    }
    
    response = requests.get(url, headers=headers, params=params)
    print_response(f"TEST 5: Get Known Sentences (pattern_id={pattern_id})", response)

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("WRITING PRACTICE API TEST SUITE")
    print("="*60)
    
    # You need to provide a valid pattern_id that exists in your database
    pattern_id = input("\nEnter a valid sentence pattern ID to test: ")
    
    try:
        pattern_id = int(pattern_id)
    except ValueError:
        print("Invalid pattern ID. Please enter a number.")
        return
    
    # Test 1: Get unknown sentences
    sentence_id = test_get_unknown_sentences(pattern_id)
    
    if sentence_id:
        # Test 2: Update sentence to 'known' (correct answer)
        test_update_sentence_correct(sentence_id)
        
        # Test 3: Increment mistakes (incorrect answer)
        # Note: This will fail if sentence is already 'known' from test 2
        # You may want to use a different sentence_id
        test_update_sentence_incorrect(sentence_id)
    else:
        print("\n⚠️  No unknown sentences found. Skipping update tests.")
    
    # Test 4: Get all sentences
    test_get_all_sentences(pattern_id)
    
    # Test 5: Get known sentences
    test_get_known_sentences(pattern_id)
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("""
    ⚠️  IMPORTANT: Before running this test:
    1. Make sure the backend server is running (python run.py)
    2. Replace FIREBASE_TOKEN with a valid token
    3. Have at least one sentence pattern with sentences in the database
    """)
    
    proceed = input("Do you want to proceed? (y/n): ")
    if proceed.lower() == 'y':
        main()
    else:
        print("Test cancelled.")
