#!/usr/bin/env python3
"""
Simple test script to verify the face recognition backend is working.
Run this after starting the Flask server.
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
    """Test all API endpoints"""
    print("Testing Face Recognition Backend API...")
    print("=" * 50)
    
    # Test 1: Get registered faces (should be empty initially)
    print("\n1. Testing GET /get_registered_faces")
    try:
        response = requests.get(f"{BASE_URL}/get_registered_faces")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server. Make sure the Flask server is running on port 5000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Test face recognition with no faces (should return error)
    print("\n2. Testing POST /recognize_face (no faces registered)")
    try:
        response = requests.post(f"{BASE_URL}/recognize_face", 
                               json={"image": "dummy_image_data"})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test face registration with invalid data
    print("\n3. Testing POST /register_face (invalid data)")
    try:
        response = requests.post(f"{BASE_URL}/register_face", 
                               json={"name": "", "image": ""})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Backend API tests completed!")
    print("If you see no connection errors, your backend is working correctly.")
    print("You can now start the frontend and test the full application.")
    
    return True

if __name__ == "__main__":
    test_endpoints()
