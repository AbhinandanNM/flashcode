#!/usr/bin/env python3
"""
Demo script for the Duel System

This script demonstrates the competitive duel system functionality including:
- Creating duels
- Joining duels
- Bot opponents
- Solution submission and winner determination
"""

import asyncio
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, Lesson, Question, Duel, LanguageEnum, QuestionTypeEnum, DuelStatusEnum
from services.duel_service import DuelService
from auth import AuthService
from schemas import DuelCreate, CodeExecutionResponse


class MockCodeExecutionService:
    """Mock code execution service for demo purposes"""
    
    async def execute_code(self, code: str, language: str, expected_output: str = None):
        # Simple mock that returns success if code contains expected output
        is_correct = expected_output and expected_output.lower() in code.lower()
        
        return CodeExecutionResponse(
            status='success',
            stdout=expected_output if is_correct else 'Wrong output',
            stderr='',
            execution_time=0.1,
            is_correct=is_correct,
            error=None
        )


async def demo_duel_system():
    """Demonstrate the duel system functionality"""
    
    print("🎮 CodeCrafts Duel System Demo")
    print("=" * 50)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create demo users
        print("\n👥 Creating demo users...")
        
        user1 = User(
            username="alice_coder",
            email="alice@codecrafts.com",
            password_hash=AuthService.get_password_hash("password123"),
            xp=150,
            streak=5
        )
        
        user2 = User(
            username="bob_developer",
            email="bob@codecrafts.com",
            password_hash=AuthService.get_password_hash("password123"),
            xp=200,
            streak=3
        )
        
        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        
        print(f"✅ Created users: {user1.username} (XP: {user1.xp}) and {user2.username} (XP: {user2.xp})")
        
        # Create demo lesson and question
        print("\n📚 Creating demo lesson and coding question...")
        
        lesson = Lesson(
            language=LanguageEnum.PYTHON,
            title="Python Basics: Hello World",
            theory="Learn to create your first Python program that prints 'Hello World'",
            difficulty=1,
            xp_reward=25,
            order_index=1
        )
        
        db.add(lesson)
        db.commit()
        db.refresh(lesson)
        
        question = Question(
            lesson_id=lesson.id,
            type=QuestionTypeEnum.CODE,
            question_text="Write a Python program that prints 'Hello World' to the console",
            correct_answer="Hello World",
            explanation="Use the print() function to output text to the console",
            difficulty=1,
            xp_reward=15
        )
        
        db.add(question)
        db.commit()
        db.refresh(question)
        
        print(f"✅ Created lesson: '{lesson.title}' with coding question")
        
        # Initialize duel service with mock code execution
        mock_code_service = MockCodeExecutionService()
        duel_service = DuelService(db, mock_code_service)
        
        # Demo 1: Create a duel
        print("\n⚔️  Demo 1: Creating a Duel")
        print("-" * 30)
        
        duel_create = DuelCreate(question_id=question.id)
        duel = duel_service.create_duel(duel_create, user1.id)
        
        print(f"🎯 {user1.username} created duel #{duel.id}")
        print(f"   Question: {question.question_text}")
        print(f"   Status: {duel.status}")
        print(f"   Waiting for opponent...")
        
        # Demo 2: Join the duel
        print("\n🤝 Demo 2: Joining the Duel")
        print("-" * 30)
        
        joined_duel = duel_service.join_duel(duel.id, user2.id)
        
        print(f"🎮 {user2.username} joined the duel!")
        print(f"   Duel Status: {joined_duel.status}")
        print(f"   Challenger: {user1.username}")
        print(f"   Opponent: {user2.username}")
        
        # Demo 3: Get duel details
        print("\n📊 Demo 3: Duel Details")
        print("-" * 30)
        
        duel_details = duel_service.get_duel(duel.id)
        
        print(f"🏟️  Duel Arena #{duel_details.id}")
        print(f"   Challenger: {duel_details.challenger_username}")
        print(f"   Opponent: {duel_details.opponent_username}")
        print(f"   Question: {duel_details.question.question_text}")
        print(f"   Status: {duel_details.status}")
        
        # Demo 4: Submit solutions
        print("\n💻 Demo 4: Submitting Solutions")
        print("-" * 30)
        
        # Alice submits first (correct solution)
        print(f"🔥 {user1.username} submits solution...")
        alice_code = "print('Hello World')"
        print(f"   Code: {alice_code}")
        
        alice_result = await duel_service.submit_solution(
            duel_id=duel.id,
            user_id=user1.id,
            code=alice_code,
            language="python",
            time_taken=25
        )
        
        print(f"✅ Solution executed successfully!")
        print(f"   Correct: {alice_result.challenger_result.is_correct}")
        print(f"   Output: {alice_result.challenger_result.stdout}")
        
        if alice_result.winner_id:
            print(f"🏆 Winner: {alice_result.winner_username}")
            print(f"   XP Awarded: {alice_result.xp_awarded}")
        
        # Demo 5: Bot opponent system
        print("\n🤖 Demo 5: Bot Opponent System")
        print("-" * 30)
        
        # Create another duel for bot demo
        bot_duel_create = DuelCreate(question_id=question.id)
        bot_duel = duel_service.create_duel(bot_duel_create, user2.id)
        
        print(f"🎯 {user2.username} created duel #{bot_duel.id}")
        
        # Manually assign a bot (simulating the auto-assignment after timeout)
        db.query(Duel).filter(Duel.id == bot_duel.id).update({
            "opponent_id": -2,  # Bot with difficulty 2
            "status": DuelStatusEnum.ACTIVE
        })
        db.commit()
        
        bot_duel_details = duel_service.get_duel(bot_duel.id)
        
        print(f"🤖 Bot opponent assigned!")
        print(f"   Challenger: {bot_duel_details.challenger_username}")
        print(f"   Opponent: {bot_duel_details.opponent_username} (Bot)")
        print(f"   Bot Difficulty: Level 2")
        
        # Submit solution against bot
        print(f"\n💻 {user2.username} submits solution against bot...")
        bob_code = "print('Hello World')"
        print(f"   Code: {bob_code}")
        
        bot_result = await duel_service.submit_solution(
            duel_id=bot_duel.id,
            user_id=user2.id,
            code=bob_code,
            language="python",
            time_taken=18
        )
        
        print(f"✅ Solution executed!")
        print(f"   Correct: {bot_result.challenger_result.is_correct}")
        
        if bot_result.winner_id:
            if bot_result.winner_id > 0:
                print(f"🏆 Winner: {bot_result.winner_username} (Human)")
            else:
                print(f"🤖 Winner: {bot_result.winner_username} (Bot)")
            print(f"   XP Awarded: {bot_result.xp_awarded}")
        
        # Demo 6: Available duels and history
        print("\n📋 Demo 6: Duel Listings")
        print("-" * 30)
        
        # Create a waiting duel for listing demo
        waiting_duel = duel_service.create_duel(DuelCreate(question_id=question.id), user1.id)
        
        available_duels = duel_service.get_available_duels(user2.id, limit=5)
        print(f"🎮 Available duels for {user2.username}:")
        for available in available_duels:
            print(f"   #{available.id} - {available.challenger_username} - {available.question_text[:50]}...")
        
        user_history = duel_service.get_user_duels(user1.id, limit=5)
        print(f"\n📊 Duel history for {user1.username}:")
        for history in user_history:
            status_emoji = {"completed": "✅", "active": "⚔️", "waiting": "⏳"}
            emoji = status_emoji.get(history.status, "❓")
            opponent = history.opponent_username or "Waiting for opponent"
            print(f"   {emoji} #{history.id} vs {opponent} - {history.status}")
        
        print("\n🎉 Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ Duel creation and matchmaking")
        print("✅ Human vs human duels")
        print("✅ Bot opponent system")
        print("✅ Code execution and winner determination")
        print("✅ XP rewards for winners")
        print("✅ Duel listings and history")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting CodeCrafts Duel System Demo...")
    asyncio.run(demo_duel_system())