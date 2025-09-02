#!/usr/bin/env python3
"""
Demo script showing the authentication system functionality
"""
from auth import AuthService
from database import SessionLocal
from models import User
import json

def demo_auth_service():
    """Demonstrate the AuthService functionality"""
    print("🔐 CodeCrafts Authentication Service Demo")
    print("=" * 45)
    
    # Demo 1: Password hashing
    print("1. Password Hashing Demo")
    password = "mySecurePassword123"
    hashed = AuthService.get_password_hash(password)
    print(f"   Original: {password}")
    print(f"   Hashed:   {hashed[:50]}...")
    print(f"   Verify:   {AuthService.verify_password(password, hashed)}")
    print()
    
    # Demo 2: JWT Token creation
    print("2. JWT Token Demo")
    user_data = {"sub": "demouser", "role": "student"}
    access_token = AuthService.create_access_token(user_data)
    refresh_token = AuthService.create_refresh_token(user_data)
    
    print(f"   Access Token:  {access_token[:50]}...")
    print(f"   Refresh Token: {refresh_token[:50]}...")
    
    # Verify tokens
    access_payload = AuthService.verify_token(access_token)
    refresh_payload = AuthService.verify_token(refresh_token)
    
    print(f"   Access Payload:  {json.dumps(access_payload, indent=2) if access_payload else 'Invalid'}")
    print(f"   Refresh Type:    {refresh_payload.get('type') if refresh_payload else 'Invalid'}")
    print()
    
    # Demo 3: Database operations
    print("3. Database Operations Demo")
    db = SessionLocal()
    
    try:
        # Check if demo user exists
        existing_user = AuthService.get_user_by_username(db, "demouser")
        if existing_user:
            print(f"   Found existing user: {existing_user.username}")
            print(f"   XP: {existing_user.xp}, Streak: {existing_user.streak}")
        else:
            # Create demo user
            demo_user = AuthService.create_user(
                db=db,
                username="demouser",
                email="demo@codecrafts.com",
                password="demopassword123"
            )
            print(f"   Created user: {demo_user.username}")
            print(f"   Email: {demo_user.email}")
            print(f"   Initial XP: {demo_user.xp}")
            print(f"   Joined: {demo_user.joined_on}")
        
        # Test authentication
        auth_user = AuthService.authenticate_user(db, "demouser", "demopassword123")
        if auth_user:
            print(f"   ✅ Authentication successful for: {auth_user.username}")
        else:
            print("   ❌ Authentication failed")
            
    except Exception as e:
        print(f"   ❌ Database error: {e}")
    finally:
        db.close()
    
    print("\n🎯 Authentication service demo completed!")

if __name__ == "__main__":
    demo_auth_service()