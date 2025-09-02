#!/usr/bin/env python3
"""
Integration test script to verify authentication system works end-to-end
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication_flow():
    """Test the complete authentication flow"""
    print("🧪 Testing CodeCrafts Authentication System")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ Health check passed")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Server not running. Please start with: uvicorn main:app --reload --port 8000")
        return False
    
    # Test 2: User registration
    print("2. Testing user registration...")
    user_data = {
        "username": "testuser123",
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code == 200:
        user_info = response.json()
        print(f"   ✅ User registered successfully: {user_info['username']}")
        print(f"   📊 Initial XP: {user_info['xp']}, Streak: {user_info['streak']}")
    else:
        print(f"   ❌ Registration failed: {response.status_code} - {response.text}")
        return False
    
    # Test 3: User login
    print("3. Testing user login...")
    login_data = {
        "username": "testuser123",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print("   ✅ Login successful")
        print(f"   🔑 Access token received (length: {len(access_token)})")
        print(f"   🔄 Refresh token received (length: {len(refresh_token)})")
    else:
        print(f"   ❌ Login failed: {response.status_code} - {response.text}")
        return False
    
    # Test 4: Access protected endpoint
    print("4. Testing protected endpoint access...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
    if response.status_code == 200:
        profile = response.json()
        print("   ✅ Profile access successful")
        print(f"   👤 User: {profile['username']} ({profile['email']})")
        print(f"   📅 Joined: {profile['joined_on']}")
    else:
        print(f"   ❌ Profile access failed: {response.status_code} - {response.text}")
        return False
    
    # Test 5: Token refresh
    print("5. Testing token refresh...")
    refresh_data = {"refresh_token": refresh_token}
    
    response = requests.post(f"{BASE_URL}/auth/refresh", json=refresh_data)
    if response.status_code == 200:
        new_tokens = response.json()
        new_access_token = new_tokens["access_token"]
        print("   ✅ Token refresh successful")
        print(f"   🔑 New access token received (length: {len(new_access_token)})")
    else:
        print(f"   ❌ Token refresh failed: {response.status_code} - {response.text}")
        return False
    
    # Test 6: Invalid credentials
    print("6. Testing invalid credentials...")
    invalid_login = {
        "username": "testuser123",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=invalid_login)
    if response.status_code == 401:
        print("   ✅ Invalid credentials properly rejected")
    else:
        print(f"   ❌ Invalid credentials test failed: {response.status_code}")
        return False
    
    # Test 7: Duplicate registration
    print("7. Testing duplicate registration...")
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code == 400:
        print("   ✅ Duplicate registration properly rejected")
    else:
        print(f"   ❌ Duplicate registration test failed: {response.status_code}")
        return False
    
    print("\n🎉 All authentication tests passed!")
    print("✨ Authentication system is working correctly!")
    return True

if __name__ == "__main__":
    test_authentication_flow()