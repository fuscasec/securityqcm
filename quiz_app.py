import json
import random
import os
import argparse
import time
import sys
from datetime import datetime

# --- PLATFORM SPECIFIC SETUP ---
try:
    import msvcrt # Windows
    PLATFORM = 'win'
except ImportError:
    import select # Linux/Mac
    import tty
    import termios
    PLATFORM = 'unix'

# --- SETTINGS ---
DEFAULT_FILENAME = "qcm.json"

def print_banner():
    print(r"""
    ###############################################################
    #                                                             #
    #              SECURITY+ SY0-701 PRACTICE EXAM                #
    #                                                             #
    ###############################################################
    #                                                             #
    #        Created by: Omar Housni                              #
    #        GitHub: https://github.com/ohousni/securityqcm       #
    #                                                             #
    ###############################################################
    """)

def load_questions(filename):
    if not os.path.exists(filename):
        print(f"[!] Error: '{filename}' not found.")
        return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[!] Error loading file: {e}")
        return []

def get_answer_text(answer_key, options):
    keys = [k.strip() for k in answer_key.split(',')]
    results = []
    for k in keys:
        text = options.get(k, "Unknown Option")
        results.append(f"{k} ({text})")
    return " & ".join(results)

def timed_input_visual(timeout):
    """
    Shows a countdown AND the user's current input on the same line.
    """
    start_time = time.time()
    user_buffer = []

    print("") # Start on a fresh line

    old_settings = None
    if PLATFORM == 'unix':
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    try:
        while True:
            elapsed = time.time() - start_time
            remaining = timeout - elapsed

            if remaining <= 0:
                sys.stdout.write("\r" + " " * 80 + "\r")
                sys.stdout.flush()
                return None

            current_str = "".join(user_buffer)
            display = f"\r⏳ Time: {int(remaining):02d}s | Answer: {current_str}"
            sys.stdout.write(display)
            sys.stdout.flush()

            char = None
            if PLATFORM == 'win':
                if msvcrt.kbhit():
                    char_code = msvcrt.getwch()
                    if char_code in ('\r', '\n'): char = 'ENTER'
                    elif char_code == '\x08': char = 'BACKSPACE'
                    else:
                        if isinstance(char_code, bytes): char = char_code.decode('utf-8', 'ignore')
                        else: char = str(char_code)
            elif PLATFORM == 'unix':
                r, _, _ = select.select([sys.stdin], [], [], 0.1)
                if r:
                    char_code = sys.stdin.read(1)
                    if char_code == '\n': char = 'ENTER'
                    elif char_code == '\x7f': char = 'BACKSPACE'
                    else: char = char_code

            if char == 'ENTER': break
            elif char == 'BACKSPACE':
                if user_buffer: user_buffer.pop()
            elif char: user_buffer.append(char)

            if PLATFORM == 'win': time.sleep(0.05)

    finally:
        if PLATFORM == 'unix':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print()

    return "".join(user_buffer).strip().upper()

def save_report(score, total_questions, weighted_score, history, custom_path=None):
    # Logic:
    # If custom_path is set -> Use that exact file path.
    # If custom_path is None -> Create 'results/' folder and use timestamped name.

    if custom_path:
        full_path = custom_path
        # Ensure the directory exists (e.g., if path is 'logs/exam1.txt', ensure 'logs/' exists)
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError as e:
                print(f"[!] Error creating directory '{directory}': {e}")
                return
    else:
        # Default behavior
        directory = "results"
        if not os.path.exists(directory):
            os.makedirs(directory)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        full_path = os.path.join(directory, f"result_{timestamp}.txt")

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write("#####################################################\n")
            f.write(f"           SECURITY+ EXAM REPORT\n")
            f.write(f"           Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("#####################################################\n\n")

            f.write(f"RAW SCORE:      {score}/{total_questions}\n")
            f.write(f"WEIGHTED SCORE: {weighted_score:.2f}/100\n")
            f.write("-" * 50 + "\n\n")

            f.write("--- WRONG / TIMEOUT ANSWERS ---\n")
            wrong_count = 0
            for item in history:
                if item['status'] != 'CORRECT':
                    wrong_count += 1
                    f.write(f"Q{item['index']}: {item['question']}\n")
                    f.write(f"    Your Answer:    {item['user_answer']} ({item['status']})\n")
                    f.write(f"    Correct Answer: {item['correct_answer']}\n")
                    f.write("-" * 50 + "\n")

            if wrong_count == 0:
                f.write("None! Perfect run.\n")

        print(f"\n[+] Report saved to: {os.path.abspath(full_path)}")
    except Exception as e:
        print(f"[!] Error saving report: {e}")

def run_quiz(filename, time_limit, num_questions, output_file):
    print_banner()

    if filename == DEFAULT_FILENAME and not os.path.exists(DEFAULT_FILENAME):
        print(f"[!] Default file '{DEFAULT_FILENAME}' not found.")
        print("    Please provide a path using -q")
        return

    all_questions = load_questions(filename)
    if not all_questions: return

    if num_questions > len(all_questions):
        num_questions = len(all_questions)

    quiz_batch = random.sample(all_questions, num_questions)
    points_per_question = 100 / num_questions

    score = 0
    history = []

    print(f"\n--- Starting Quiz ({num_questions} Questions) ---")
    if time_limit:
        print(f"--- TIMED MODE: {time_limit}s per question ---")
    else:
        print("--- MODE: Unlimited Time ---")

    print("-" * 50 + "\n")

    for index, q in enumerate(quiz_batch, 1):
        print(f"Q-{index}) {q['question']}")

        valid_options = []
        for key in sorted(q['options'].keys()):
            print(f"{key}. {q['options'][key]}")
            valid_options.append(key)

        raw_correct_key = q['answer'].strip().upper()
        full_correct_display = get_answer_text(raw_correct_key, q['options'])

        user_input = ""
        status = ""

        if time_limit:
            result = timed_input_visual(time_limit)
            if result is None:
                print(f"[!] TIME'S UP!")
                print(f"    Correct: {full_correct_display}")
                status = "TIMEOUT"
                user_input = "TIMEOUT"
            else:
                user_input = result
        else:
            user_input = input("Enter answer: ").strip().upper()

        if status != "TIMEOUT":
            if user_input == raw_correct_key:
                print(f">> Correct! (+{points_per_question:.1f} pts)")
                score += 1
                status = "CORRECT"
            else:
                print(f">> Wrong! Correct: {full_correct_display}")
                status = "WRONG"

        print("-" * 50)

        history.append({
            'index': index,
            'question': q['question'],
            'user_answer': user_input,
            'correct_answer': full_correct_display,
            'status': status
        })

    weighted_score = score * points_per_question
    print(f"\n--- Quiz Finished ---")
    print(f"Raw Score:      {score}/{num_questions}")
    print(f"Weighted Score: {weighted_score:.2f}/100")

    save_report(score, num_questions, weighted_score, history, output_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiz", default=DEFAULT_FILENAME, help="Path to JSON")
    parser.add_argument("-t", "--time", type=int, default=None, help="Seconds per question")
    parser.add_argument("-n", "--number", type=int, default=100, help="Number of questions")

    # UPDATED: -o now takes a FILE path, default is None
    parser.add_argument("-o", "--output", default=None, help="Path to output file (e.g., /home/user/result.txt)")

    args = parser.parse_args()
    run_quiz(args.quiz, args.time, args.number, args.output)
