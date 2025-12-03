import json
import random
import os

def print_banner():
    """Prints the startup banner."""
    print(r"""
    ###############################################################
    #                                                             #
    #             SECURITY+ SY0-701 PRACTICE EXAM                 #
    #                                                             #
    ###############################################################
    #                                                             #
    #        Created by: Omar Housni                              #
    #        GitHub: https://github.com/ohousni/securityqcm      #
    #                                                             #
    ###############################################################
    """)

def load_questions(filename="qcm.json"):
    """Loads questions from the JSON file."""
    if not os.path.exists(filename):
        print(f"[!] Error: '{filename}' not found. Please ensure the file exists.")
        return []

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("[!] Error: JSON format is incorrect (expected a list of questions).")
                return []
    except Exception as e:
        print(f"[!] Error loading file: {e}")
        return []

def run_quiz():
    # Print the banner
    print_banner()

    # 1. Load the data
    all_questions = load_questions()

    if not all_questions:
        return

    # 2. Settings
    total_quiz_questions = 100

    # Ensure we don't crash if the file has fewer than 100 questions
    if len(all_questions) < total_quiz_questions:
        print(f"[!] Warning: Only {len(all_questions)} questions available. Adjusting quiz size.")
        total_quiz_questions = len(all_questions)

    # 3. Select unique random questions
    # random.sample guarantees unique selection (no duplicates in one session)
    quiz_batch = random.sample(all_questions, total_quiz_questions)

    score = 0
    print(f"\n--- Starting Quiz ({total_quiz_questions} Questions) ---")
    print("Type the letter (A, B, C, D...) corresponding to the correct answer.\n")

    # 4. Main Quiz Loop
    for index, q in enumerate(quiz_batch, 1):
        print(f"Q-{index}) {q['question']}")

        # specific handling to ensure options print in order A, B, C, D...
        # We look for keys 'A', 'B', 'C', 'D', 'E', 'F' specifically
        valid_options = []
        for key in sorted(q['options'].keys()):
            print(f"{key}. {q['options'][key]}")
            valid_options.append(key)

        # Get user input
        while True:
            user_answer = input("enter your answer : ").strip().upper()
            if user_answer in valid_options:
                break
            print(f"Invalid input. Please enter one of: {', '.join(valid_options)}")

        # Check answer
        # Some JSONs might have the answer as "A" or "A, B".
        # We strip spaces just in case.
        correct_answer = q['answer'].strip().upper()

        # Simple check for exact match
        # (If the question requires multiple answers like 'A, B', the user must type 'A, B' exactly or you can adapt logic)
        # For this script, we assume single letter input usually, or exact string match.

        if user_answer == correct_answer:
            print("your answer is correct")
            score += 1
        else:
            print(f"your answer is not correct the correct answer is : {correct_answer}")

        print("-" * 40) # Separator line

    # 5. Final Result
    print(f"\n--- Quiz Finished ---")
    print(f"Final Score: {score}/{total_quiz_questions}")

    if score == total_quiz_questions:
        print("Perfect Score! Excellent work.")
    elif score >= 80:
        print("Great job! You passed.")
    else:
        print("Keep practicing!")

if __name__ == "__main__":
    run_quiz()
