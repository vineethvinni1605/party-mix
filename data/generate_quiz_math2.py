import json
import random
from pathlib import Path

random.seed(108)
questions = []
seen = set()

def add_question(question, correct, wrong, difficulty):
    key = question.strip().lower()
    if key in seen:
        return

    options = [correct] + wrong
    if len(set(options)) != 4:
        return

    random.shuffle(options)
    questions.append({
        "q": question,
        "options": [str(x) for x in options],
        "answer": options.index(correct),
        "category": "Math & logic",
        "difficulty": difficulty
    })
    seen.add(key)

# 25 multiplication questions
for a in range(13, 38):
    b = (a % 9) + 6
    correct = a * b
    add_question(
        f"What is {a} multiplied by {b}?",
        correct,
        [correct + b, correct - b, correct + a],
        "medium"
    )

# 25 division questions
for a in range(12, 37):
    divisor = (a % 8) + 3
    correct = a
    dividend = a * divisor
    add_question(
        f"What is {dividend} divided by {divisor}?",
        correct,
        [correct + 1, correct - 2, correct + 3],
        "easy"
    )

# 25 number sequence questions
for a in range(5, 30):
    step = (a % 7) + 3
    correct = a + 4 * step
    add_question(
        f"Complete the sequence: {a}, {a+step}, {a+2*step}, {a+3*step}, ?",
        correct,
        [correct + step, correct - step, correct + 2*step],
        "medium"
    )

# 25 square questions
for a in range(16, 41):
    correct = a * a
    add_question(
        f"What is the square of {a}?",
        correct,
        [correct + a, correct - a, correct + 2*a],
        "medium"
    )

assert len(questions) == 100

output = Path(__file__).parent / "quiz_batch8.json"
output.write_text(json.dumps(questions, indent=2), encoding="utf-8")

print("Generated:", len(questions), "questions")
print("Saved to:", output)
