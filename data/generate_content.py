
import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
DRAWING_FILE = DATA_DIR / "drawing.json"

# Objects that players can draw
objects = [
    "cat", "dog", "robot", "penguin", "elephant",
    "dinosaur", "dragon", "astronaut", "pirate",
    "superhero", "monkey", "rabbit", "tiger",
    "panda", "alien", "snowman", "wizard",
    "cricket player", "football player", "gamer"
]

# Actions to make drawing challenges interesting
actions = [
    "riding a bicycle",
    "eating pizza",
    "playing cricket",
    "dancing",
    "flying a kite",
    "playing video games",
    "driving a car",
    "sleeping on a sofa",
    "cooking dinner",
    "wearing sunglasses",
    "playing guitar",
    "reading a book",
    "surfing",
    "climbing a mountain",
    "holding an umbrella"
]

with open(DRAWING_FILE, "r", encoding="utf-8") as file:
    existing = json.load(file)

# Remember existing prompts to prevent duplicates
seen = {
    item["prompt"].strip().lower()
    for item in existing
}

new_challenges = []

for obj in objects:
    for action in actions:
        prompt = f"A {obj} {action}"

        if prompt.lower() in seen:
            continue

        seen.add(prompt.lower())

        new_challenges.append({
            "prompt": prompt,
            "category": "Funny & random",
            "difficulty": "medium"
        })

random.Random(42).shuffle(new_challenges)

# Add enough unique prompts to reach 300 total
needed = max(0, 300 - len(existing))
existing.extend(new_challenges[:needed])

with open(DRAWING_FILE, "w", encoding="utf-8") as file:
    json.dump(existing, file, indent=2, ensure_ascii=False)

print(f"Drawing challenges: {len(existing)}")
print(f"New challenges added: {min(needed, len(new_challenges))}")

# ==========================================
# GUESS THE WORD CONTENT GENERATOR
# ==========================================

WORDS_FILE = DATA_DIR / "words.json"

word_groups = {
    "General knowledge": [
        ("LIBRARY", "A place where people borrow books"),
        ("CALENDAR", "Shows days, weeks, and months"),
        ("UMBRELLA", "Protects you from rain"),
        ("TELESCOPE", "Used to observe distant objects"),
        ("COMPASS", "Helps you find directions"),
        ("PASSPORT", "Document used for international travel"),
        ("KEYBOARD", "Used to type on a computer"),
        ("BACKPACK", "A bag carried on your shoulders")
    ],
    "Sports": [
        ("BADMINTON", "A racket sport played with a shuttlecock"),
        ("FOOTBALL", "A sport played with a ball and goals"),
        ("TENNIS", "A racket sport played across a net"),
        ("OLYMPICS", "International sporting event held every four years"),
        ("WICKET", "Three stumps used in cricket"),
        ("STADIUM", "Large venue for sporting events"),
        ("MARATHON", "A running race of about 42 kilometers"),
        ("BASKETBALL", "A sport where players shoot into a hoop")
    ],
    "Science & technology": [
        ("SATELLITE", "An object that orbits a planet"),
        ("MICROSCOPE", "Used to view very small objects"),
        ("ALGORITHM", "A sequence of steps to solve a problem"),
        ("ROBOTICS", "The study and design of robots"),
        ("DATABASE", "An organized collection of information"),
        ("GRAVITY", "Force that attracts objects toward each other"),
        ("BLUETOOTH", "Technology for short-range wireless connections"),
        ("BATTERY", "A device that stores electrical energy")
    ],
    "Geography": [
        ("EVEREST", "The world's highest mountain above sea level"),
        ("SAHARA", "A vast desert in North Africa"),
        ("AMAZON", "A major river in South America"),
        ("ANTARCTICA", "The coldest continent"),
        ("PACIFIC", "The largest ocean on Earth"),
        ("HIMALAYAS", "Mountain range containing Mount Everest"),
        ("NILE", "A famous river flowing through Egypt"),
        ("TOKYO", "The capital of Japan")
    ],
    "Indian movies & culture": [
        ("BOLLYWOOD", "Hindi-language film industry based in Mumbai"),
        ("DIWALI", "Indian festival known for lights"),
        ("BIRYANI", "A popular spiced rice dish"),
        ("KOLLYWOOD", "Tamil-language film industry"),
        ("TOLLYWOOD", "Telugu-language film industry"),
        ("KABADDI", "Team sport involving tagging opponents"),
        ("HOLI", "Indian festival associated with colors"),
        ("SITAR", "Traditional Indian string instrument")
    ],
    "Gaming & anime": [
        ("MINECRAFT", "Sandbox game known for its blocks"),
        ("NARUTO", "Anime ninja who dreams of becoming Hokage"),
        ("POKEMON", "Franchise about collecting and battling creatures"),
        ("SONIC", "Blue video game hedgehog"),
        ("ZELDA", "Princess in a Nintendo fantasy game series"),
        ("MARIO", "Nintendo character known for his red cap"),
        ("ROBLOX", "Platform for creating and playing games"),
        ("LUFFY", "Pirate captain in One Piece")
    ]
}

with open(WORDS_FILE, "r", encoding="utf-8") as file:
    existing_words = json.load(file)

seen_words = {
    item["word"].strip().upper()
    for item in existing_words
}

added_words = 0

for category, entries in word_groups.items():
    for word, hint in entries:
        if word.upper() in seen_words:
            continue

        existing_words.append({
            "word": word,
            "hint": hint,
            "category": category,
            "difficulty": "medium"
        })

        seen_words.add(word.upper())
        added_words += 1

with open(WORDS_FILE, "w", encoding="utf-8") as file:
    json.dump(existing_words, file, indent=2, ensure_ascii=False)

print(f"Word challenges: {len(existing_words)}")
print(f"New word challenges added: {added_words}")

# ==========================================
# VALIDATE GUESS THE WORD LIBRARY
# ==========================================

required_fields = ["word", "hint", "category", "difficulty"]

invalid_entries = []

for index, item in enumerate(existing_words, start=1):
    if not isinstance(item, dict):
        invalid_entries.append(index)
        continue

    if any(
        not isinstance(item.get(field), str)
        or not item[field].strip()
        for field in required_fields
    ):
        invalid_entries.append(index)

unique_count = len({
    item["word"].strip().upper()
    for item in existing_words
    if isinstance(item, dict)
    and isinstance(item.get("word"), str)
})

print("\n--- WORD LIBRARY VALIDATION ---")
print("Total words:", len(existing_words))
print("Unique words:", unique_count)
print("Invalid entries:", len(invalid_entries))

if invalid_entries:
    print("Invalid entry numbers:", invalid_entries)
elif unique_count != len(existing_words):
    print("WARNING: Duplicate words found!")
else:
    print("PASS: All word entries are valid and unique!")
