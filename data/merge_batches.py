
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent

GAME_FIELDS = {
    "quiz": "q",
    "words": "word",
    "drawing": "prompt",
    "spy": "word",
    "speed": "q"
}

for game, unique_field in GAME_FIELDS.items():
    main_file = DATA_DIR / f"{game}.json"
    batch_files = sorted(DATA_DIR.glob(f"{game}_batch*.json"))

    main = json.loads(main_file.read_text(encoding="utf-8"))
    seen = {
        str(item[unique_field]).strip().casefold()
        for item in main
    }

    added = 0

    for batch_file in batch_files:
        batch = json.loads(batch_file.read_text(encoding="utf-8"))

        for item in batch:
            key = str(item[unique_field]).strip().casefold()

            if not key or key in seen:
                continue

            main.append(item)
            seen.add(key)
            added += 1

    if added:
        main_file.write_text(
            json.dumps(main, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )

    print(f"{game}: {len(main)} total, {added} newly added")
