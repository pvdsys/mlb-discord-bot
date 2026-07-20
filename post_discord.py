#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen


def main():
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")

    if not webhook:
        print("DISCORD_WEBHOOK_URL is not set", file=sys.stderr)
        return 2

    card = json.loads(
        Path("card.json").read_text(encoding="utf-8")
    )

    fields = []

    for section in card["sections"]:
        rows = section.get("rows", [])

        if rows:
            value = "\n".join(
                f"**{row['player']}** — {row['bet']} · **{row['odds']}**"
                f" · 🕒 **{row.get('start_time', 'TBD')} ET**"
                + (
                    f"\n{row['note']}"
                    if row.get("note")
                    else ""
                )
                for row in rows
            )
        else:
            value = "None — no qualifying plays."

        fields.append({
            "name": section["name"],
            "value": value[:1024],
            "inline": False
        })

    payload = {
        "username": "MLB Model",
        "embeds": [{
            "title": f"⚾ MLB Model — {card['date']}",
            "description": card["description"],
            "color": 3066993,
            "fields": fields,
            "footer": {
                "text": card["footer"]
            }
        }]
    }

    request = Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "MLB-Model/1.0"
        },
        method="POST"
    )

    with urlopen(request, timeout=20) as response:
        print(f"Discord returned {response.status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
