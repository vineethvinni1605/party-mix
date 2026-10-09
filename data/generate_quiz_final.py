import json
import random
from pathlib import Path

random.seed(114)
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

# 25 money calculations
for a in range(12, 37):
    price = a * 5
    correct = price * 3
    add_question(
        f"If one ticket costs ${price}, how much do 3 tickets cost?",
        correct,
        [correct + price, correct - price, correct + 10],
        "easy"
    )

# 25 fraction questions
for a in range(10, 35):
    number = a * 8
    correct = number // 8
    add_question(
        f"What is one-eighth of {number}?",
        correct,
        [correct + 2, correct - 2, correct + 4],
        "medium"
    )

# 25 rectangle perimeter questions
for a in range(8, 33):
    length = a + 6
    width = a
    correct = 2 * (length + width)
    add_question(
        f"What is the perimeter of a rectangle with length {length} cm and width {width} cm?",
        correct,
        [correct + 4, correct - 4, correct + 8],
        "medium"
    )

# 25 number reasoning questions
for a in range(11, 36):
    correct = a * 3 + 7
    add_question(
        f"What is 3 times {a}, plus 7?",
        correct,
        [correct + 3, correct - 7, correct + 7],
        "medium"
    )

assert len(questions) == 100

output = Path(__file__).parent / "quiz_batch10.json"
output.write_text(
    json.dumps(questions, indent=2),
    encoding="utf-8"
)

print("Generated:", len(questions), "questions")
print("Saved to:", output)
