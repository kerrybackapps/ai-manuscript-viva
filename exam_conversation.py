"""
Exam Conversation Module
Conducts structured oral exam conversations with students
"""
import os
from anthropic import Anthropic
from typing import List, Dict

class ExamConversation:
    """Manages the exam conversation flow"""

    def __init__(self, student_name: str, exam_context: str):
        self.student_name = student_name
        self.exam_context = exam_context
        self.conversation_history: List[Dict[str, str]] = []
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def get_exam_prompt(self) -> str:
        """Generate the system prompt for the exam"""
        return f"""You are an AI examiner conducting an oral exam.

EXAM CONTEXT:
{self.exam_context}

INSTRUCTIONS:
- Ask ONE question at a time
- Ask probing follow-up questions to test understanding
- Be patient and allow think time
- If student asks you to repeat, repeat the question verbatim
- Conduct 5-7 questions total to assess understanding
- End the exam when you have sufficient information

Keep questions focused on:
1. Understanding of core concepts
2. Ability to explain rationale
3. Recognition of limitations and failure modes
4. Application of knowledge to scenarios

After each student response, either:
- Ask a follow-up question, OR
- Move to the next topic, OR
- Conclude the exam with "EXAM_COMPLETE"

Current student: {self.student_name}
"""

    def conduct_exam(self) -> str:
        """Run the interactive exam conversation"""
        print(f"\n{'='*60}")
        print(f"ORAL EXAM - Student: {self.student_name}")
        print(f"{'='*60}\n")

        system_prompt = self.get_exam_prompt()

        # Initialize conversation
        messages = [
            {"role": "user", "content": "Begin the exam."}
        ]

        exam_active = True
        question_count = 0

        while exam_active and question_count < 10:
            # Get examiner's question
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                system=system_prompt,
                messages=messages
            )

            examiner_message = response.content[0].text

            # Check if exam is complete
            if "EXAM_COMPLETE" in examiner_message:
                print("\nExaminer: Thank you. The exam is now complete.\n")
                exam_active = False
                break

            print(f"\nExaminer: {examiner_message}\n")

            # Record the question
            self.conversation_history.append({
                "role": "examiner",
                "content": examiner_message
            })

            # Get student response
            student_response = input(f"{self.student_name}: ").strip()

            # Handle special commands
            if student_response.lower() in ['quit', 'exit']:
                print("\nExam terminated by student.\n")
                break

            if student_response.lower() in ['repeat', 'again', 'repeat question']:
                print(f"\nExaminer (repeating): {examiner_message}\n")
                student_response = input(f"{self.student_name}: ").strip()

            # Record student response
            self.conversation_history.append({
                "role": "student",
                "content": student_response
            })

            # Update conversation for next turn
            messages.append({"role": "assistant", "content": examiner_message})
            messages.append({"role": "user", "content": student_response})

            question_count += 1

        return self.get_transcript()

    def get_transcript(self) -> str:
        """Generate a formatted transcript of the exam"""
        transcript = f"EXAM TRANSCRIPT\n"
        transcript += f"Student: {self.student_name}\n"
        transcript += f"{'='*60}\n\n"

        for entry in self.conversation_history:
            role = "EXAMINER" if entry["role"] == "examiner" else self.student_name.upper()
            transcript += f"{role}: {entry['content']}\n\n"

        return transcript
