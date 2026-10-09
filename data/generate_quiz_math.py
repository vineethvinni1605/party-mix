
import json
import random
from pathlib import Path

random.seed(42)

questions = []
seen = set()

def add_question(question, correct, wrong, difficulty):
    if question.lower() in seen:
        return

    options = [correct] + wrong
    if len(set(options)) != 4:
        return

    random.shuffle(options)

    questions.append({
        "q": question,
        "options": [str(x) for x in options],
        "answer": options.index(correct),
        "category": "General knowledge",
        "difficulty": difficulty
    })
    seen.add(question.lower())


# 25 addition questions
for a in range(12, 37):
    b = a + 17
    correct = a + b
    add_question(
        f"What is {a} + {b}?",
        correct,
        [correct - 2, correct + 3, correct + 5],
        "easy"
    )

# 25 multiplication questions
for a in range(6, 31):
    b = (a % 7) + 3
    correct = a * b
    add_question(
        f"What is {a} × {b}?",
        correct,
        [correct + b, correct - b, correct + 2 * b],
        "medium"
    )

# 25 subtraction questions
for a in range(50, 75):
    b = (a % 19) + 11
    correct = a - b
    add_question(
        f"What is {a} - {b}?",
        correct,
        [correct + 2, correct - 3, correct + 5],
        "easy"
    )

# 25 percentage questions
for a in range(1, 26):
    number = a * 20
    correct = number // 4
    add_question(
        f"What is 25% of {number}?",
        correct,
        [correct + 5, correct + 10, correct - 5],
        "medium"
    )

assert len(questions) == 100, "Expected exactly 100 questions"

output = Path(__file__).parent / "quiz_batch3.json"
output.write_text(
    json.dumps(questions, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

print("Generated:", len(questions), "questions")
print("Saved to:", output)

