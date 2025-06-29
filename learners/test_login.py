#!/usr/bin/env python3
"""
Test login endpoint and show response details
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_login():
    """Test login and show response details"""
    
    print("Testing Login Endpoint...")
    print("=" * 40)
    
    # Test login
    login_data = {
        "username": "student0",
        "password": "password123"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login/",
            json=login_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for header, value in response.headers.items():
            print(f"  {header}: {value}")
        
        print(f"\nResponse Body:")
        try:
            body = response.json()
            print(json.dumps(body, indent=2))
        except:
            print(response.text)
        
        print(f"\nCookies:")
        for cookie in response.cookies:
            print(f"  {cookie.name}: {cookie.value}")
            
        # Test if we can access protected endpoint with session
        if response.status_code == 200:
            print(f"\nTesting protected endpoint with session...")
            
            # Use the same session
            session = requests.Session()
            session.cookies.update(response.cookies)
            
            # Try to get courses
            courses_response = session.get(f"{BASE_URL}/courses/")
            print(f"Courses endpoint status: {courses_response.status_code}")
            
            if courses_response.status_code == 200:
                courses = courses_response.json()
                print(f"Found {len(courses)} courses")
            else:
                print(f"Error: {courses_response.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login() 