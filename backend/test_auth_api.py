import requests
import json

# API base URL
BASE_URL = 'http://localhost:8000/api'

def test_login(email, password):
    """Test the login endpoint"""
    url = f"{BASE_URL}/auth/login/"
    data = {
        'email': email,
        'password': password
    }
    
    response = requests.post(url, data=data)
    print(f"Login Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Token: {result['token']}")
        print(f"User: {json.dumps(result['user'], indent=2)}")
        return result['token']
    else:
        print(f"Error: {response.text}")
        return None

def test_user_detail(token):
    """Test the user detail endpoint"""
    url = f"{BASE_URL}/auth/user/"
    headers = {'Authorization': f'Token {token}'}
    
    response = requests.get(url, headers=headers)
    print(f"\nUser Detail Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"User Detail: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: {response.text}")

def test_issues_list(token):
    """Test the issues list endpoint"""
    url = f"{BASE_URL}/issues/"
    headers = {'Authorization': f'Token {token}'}
    
    response = requests.get(url, headers=headers)
    print(f"\nIssues List Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Issues Count: {len(result)}")
        if len(result) > 0:
            print(f"First Issue: {json.dumps(result[0], indent=2)}")
    else:
        print(f"Error: {response.text}")

# Replace with your admin user's email and password
email = "admin@example.com"  # Replace with actual email
password = "your_password"   # Replace with actual password

print("Testing Authentication API...")
token = test_login(email, password)

if token:
    test_user_detail(token)
    test_issues_list(token)
