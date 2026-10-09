import json
import random
from pathlib import Path

random.seed(112)
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

# 25 percentage questions
for a in range(11, 36):
    number = a * 40
    correct = number * 15 // 100
    add_question(
        f"What is 15% of {number}?",
        correct,
        [correct + 10, correct - 10, correct + 20],
        "medium"
    )

# 25 average questions
for a in range(10, 35):
    numbers = [a, a + 8, a + 16]
    correct = a + 8
    add_question(
        f"What is the average of {numbers[0]}, {numbers[1]}, and {numbers[2]}?",
        correct,
        [correct + 4, correct - 4, correct + 8],
        "medium"
    )

# 25 time conversion questions
for a in range(15, 40):
    hours = a
    correct = hours * 60
    add_question(
        f"How many minutes are in {hours} hours?",
        correct,
        [correct + 30, correct - 60, correct + 60],
        "easy"
    )

# 25 number pattern questions
for a in range(8, 33):
    correct = a * 5
    add_question(
        f"What is the fifth multiple of {a}?",
        correct,
        [a * 4, a * 6, a * 7],
        "medium"
    )

assert len(questions) == 100

output = Path(__file__).parent / "quiz_batch9.json"
output.write_text(
    json.dumps(questions, indent=2),
    encoding="utf-8"
)

print("Generated:", len(questions), "questions")
print("Saved to:", output)
