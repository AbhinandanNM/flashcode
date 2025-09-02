#!/usr/bin/env python3
"""
Script to create sample questions for testing the question system
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, Lesson, Question, LanguageEnum, QuestionTypeEnum
import json

# Create database tables
Base.metadata.create_all(bind=engine)

def create_sample_questions():
    db = SessionLocal()
    
    try:
        # Check if we already have a lesson to add questions to
        lesson = db.query(Lesson).filter(Lesson.title.like("%Python%")).first()
        
        if not lesson:
            # Create a sample lesson
            lesson = Lesson(
                language=LanguageEnum.PYTHON,
                title="Python Loops",
                theory="Loops in Python allow you to repeat code. There are two main types: 'for' loops for iterating over sequences, and 'while' loops for repeating while a condition is true.",
                difficulty=2,
                xp_reward=50,
                order_index=1,
                is_published=True
            )
            db.add(lesson)
            db.commit()
            db.refresh(lesson)
            print(f"Created lesson: {lesson.title}")
        
        # Sample MCQ Question
        mcq_question = Question(
            lesson_id=lesson.id,
            type=QuestionTypeEnum.MCQ,
            question_text="Which loop is used to iterate over a sequence in Python?",
            options={
                "A": "for loop",
                "B": "while loop", 
                "C": "do-while loop",
                "D": "repeat loop"
            },
            correct_answer="A",
            explanation="The 'for' loop is specifically designed to iterate over sequences like lists, strings, and ranges.",
            difficulty=1,
            xp_reward=10
        )
        
        # Sample Fill-in-the-blank Question
        fill_blank_question = Question(
            lesson_id=lesson.id,
            type=QuestionTypeEnum.FILL_BLANK,
            question_text="Complete the code to create a loop from 0 to 4: for i in _____(5):",
            options=None,
            correct_answer="range",
            explanation="The range() function generates a sequence of numbers from 0 to n-1.",
            difficulty=2,
            xp_reward=15
        )
        
        # Sample Flashcard Question
        flashcard_question = Question(
            lesson_id=lesson.id,
            type=QuestionTypeEnum.FLASHCARD,
            question_text="What does 'break' do in a loop?",
            options=None,
            correct_answer="exits the loop immediately",
            explanation="The 'break' statement terminates the current loop and continues execution after the loop.",
            difficulty=2,
            xp_reward=10
        )
        
        # Sample Code Question
        code_question = Question(
            lesson_id=lesson.id,
            type=QuestionTypeEnum.CODE,
            question_text="Write a for loop that prints numbers from 1 to 3:",
            options=None,
            correct_answer="for i in range(1, 4):\n    print(i)",
            explanation="Use range(1, 4) to get numbers 1, 2, 3 and print each one.",
            difficulty=3,
            xp_reward=25
        )
        
        # Add all questions
        questions = [mcq_question, fill_blank_question, flashcard_question, code_question]
        db.add_all(questions)
        db.commit()
        
        print(f"Created {len(questions)} sample questions for lesson '{lesson.title}':")
        for q in questions:
            print(f"  - {q.type.value}: {q.question_text[:50]}...")
        
        print(f"\nLesson ID: {lesson.id}")
        print("You can now test the question system using these sample questions!")
        
    except Exception as e:
        print(f"Error creating sample questions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_questions()