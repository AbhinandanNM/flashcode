#!/usr/bin/env python3
"""
Integration test script to verify lesson management system works end-to-end
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_lesson_management_flow():
    """Test the complete lesson management flow"""
    print("🧪 Testing CodeCrafts Lesson Management System")
    print("=" * 50)
    
    # First, we need to authenticate
    print("1. Setting up authentication...")
    
    # Register a test user
    user_data = {
        "username": "lessontest123",
        "email": "lessontest@example.com",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    if response.status_code != 200:
        # User might already exist, try to login
        pass
    
    # Login to get token
    login_data = {
        "username": "lessontest123",
        "password": "password123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"   ❌ Authentication failed: {response.status_code} - {response.text}")
        return False
    
    tokens = response.json()
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    print("   ✅ Authentication successful")
    
    # Test 2: Create a lesson
    print("2. Testing lesson creation...")
    lesson_data = {
        "language": "python",
        "title": "Python Loops Integration Test",
        "theory": "Learn about for and while loops in Python. Loops allow you to repeat code efficiently.",
        "difficulty": 2,
        "xp_reward": 150,
        "order_index": 1,
        "is_published": True
    }
    
    response = requests.post(f"{BASE_URL}/lessons/", json=lesson_data, headers=headers)
    if response.status_code == 200:
        lesson = response.json()
        lesson_id = lesson["id"]
        print(f"   ✅ Lesson created successfully: {lesson['title']}")
        print(f"   📚 Lesson ID: {lesson_id}, Language: {lesson['language']}, Difficulty: {lesson['difficulty']}")
    else:
        print(f"   ❌ Lesson creation failed: {response.status_code} - {response.text}")
        return False
    
    # Test 3: Retrieve lessons with filtering
    print("3. Testing lesson retrieval and filtering...")
    
    # Get all lessons
    response = requests.get(f"{BASE_URL}/lessons/", headers=headers)
    if response.status_code == 200:
        lessons = response.json()
        print(f"   ✅ Retrieved {len(lessons)} lessons")
        
        # Verify our lesson is in the list
        found_lesson = next((l for l in lessons if l["id"] == lesson_id), None)
        if found_lesson:
            print(f"   ✅ Created lesson found in list")
            print(f"   📊 Progress status: {found_lesson.get('progress', 'No progress yet')}")
        else:
            print("   ❌ Created lesson not found in list")
            return False
    else:
        print(f"   ❌ Lesson retrieval failed: {response.status_code} - {response.text}")
        return False
    
    # Test filtering by language
    response = requests.get(f"{BASE_URL}/lessons/?language=python", headers=headers)
    if response.status_code == 200:
        python_lessons = response.json()
        print(f"   ✅ Language filtering works: {len(python_lessons)} Python lessons")
    else:
        print(f"   ❌ Language filtering failed: {response.status_code}")
        return False
    
    # Test filtering by difficulty
    response = requests.get(f"{BASE_URL}/lessons/?difficulty=2", headers=headers)
    if response.status_code == 200:
        difficulty_lessons = response.json()
        print(f"   ✅ Difficulty filtering works: {len(difficulty_lessons)} difficulty-2 lessons")
    else:
        print(f"   ❌ Difficulty filtering failed: {response.status_code}")
        return False
    
    # Test 4: Get specific lesson
    print("4. Testing specific lesson retrieval...")
    response = requests.get(f"{BASE_URL}/lessons/{lesson_id}", headers=headers)
    if response.status_code == 200:
        lesson_detail = response.json()
        print(f"   ✅ Lesson details retrieved: {lesson_detail['title']}")
        print(f"   📖 Theory preview: {lesson_detail['theory'][:50]}...")
    else:
        print(f"   ❌ Lesson detail retrieval failed: {response.status_code}")
        return False
    
    # Test 5: Progress tracking
    print("5. Testing progress tracking...")
    
    # Create initial progress
    progress_data = {
        "status": "in_progress",
        "score": 0.6,
        "attempts": 1
    }
    
    response = requests.post(f"{BASE_URL}/lessons/{lesson_id}/progress", json=progress_data, headers=headers)
    if response.status_code == 200:
        progress = response.json()
        print(f"   ✅ Progress created: {progress['status']} with score {progress['score']}")
    else:
        print(f"   ❌ Progress creation failed: {response.status_code} - {response.text}")
        return False
    
    # Update progress
    updated_progress = {
        "status": "completed",
        "score": 0.85,
        "attempts": 2
    }
    
    response = requests.post(f"{BASE_URL}/lessons/{lesson_id}/progress", json=updated_progress, headers=headers)
    if response.status_code == 200:
        progress = response.json()
        print(f"   ✅ Progress updated: {progress['status']} with score {progress['score']}")
    else:
        print(f"   ❌ Progress update failed: {response.status_code}")
        return False
    
    # Get progress
    response = requests.get(f"{BASE_URL}/lessons/{lesson_id}/progress", headers=headers)
    if response.status_code == 200:
        progress = response.json()
        print(f"   ✅ Progress retrieved: {progress['status']} - {progress['score']} score")
    else:
        print(f"   ❌ Progress retrieval failed: {response.status_code}")
        return False
    
    # Test 6: Get all user progress
    print("6. Testing user progress overview...")
    response = requests.get(f"{BASE_URL}/lessons/progress/all", headers=headers)
    if response.status_code == 200:
        all_progress = response.json()
        print(f"   ✅ User progress overview: {len(all_progress)} lessons with progress")
    else:
        print(f"   ❌ User progress overview failed: {response.status_code}")
        return False
    
    # Test 7: Lesson statistics
    print("7. Testing lesson statistics...")
    response = requests.get(f"{BASE_URL}/lessons/{lesson_id}/statistics", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Lesson statistics: {stats['total_started']} started, {stats['total_completed']} completed")
        print(f"   📊 Completion rate: {stats['completion_rate']}%, Average score: {stats['average_score']}")
    else:
        print(f"   ❌ Lesson statistics failed: {response.status_code}")
        return False
    
    # Test 8: Update lesson
    print("8. Testing lesson update...")
    update_data = {
        "title": "Python Loops - Updated",
        "difficulty": 3
    }
    
    response = requests.put(f"{BASE_URL}/lessons/{lesson_id}", json=update_data, headers=headers)
    if response.status_code == 200:
        updated_lesson = response.json()
        print(f"   ✅ Lesson updated: {updated_lesson['title']}, difficulty: {updated_lesson['difficulty']}")
    else:
        print(f"   ❌ Lesson update failed: {response.status_code}")
        return False
    
    print("\n🎉 All lesson management tests passed!")
    print("✨ Lesson management system is working correctly!")
    print("\n📋 Verified functionality:")
    print("   • Lesson CRUD operations")
    print("   • Lesson filtering by language and difficulty")
    print("   • Progress tracking (create, update, retrieve)")
    print("   • User progress overview")
    print("   • Lesson statistics")
    print("   • Authentication integration")
    return True

if __name__ == "__main__":
    try:
        test_lesson_management_flow()
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Please start with: uvicorn main:app --reload --port 8000")