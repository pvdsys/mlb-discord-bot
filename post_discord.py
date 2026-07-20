#!/usr/bin/env python3
"""Post a JSON MLB model card to Discord using a webhook secret."""

import json
import os
import sys
from pathlib import Path
from urllib.request import Request, urlopen


def main() -> int:
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook:
        print("DISCORD_WEBHOOK_URL is not set", file=sys.stderr)
        return 2

    card_path = Path(os.environ.get("MODEL_CARD_PATH", "card.json"))
    card = json.loads(card_path.read_text(encoding="utf-8"))
    fields = []
    for section in card["sections"]:
        rows = section.get("rows", [])
        value = "\n".join(
            f"**{row['player']}** — {row['bet']} · **{row['odds']}**"
            + (f"\n{row['note']}" if row.get("note") else "")
            for row in rows
        ) or "None — no qualifying plays."
        fields.append({"name": section["name"], "value": value[:1024], "inline": False})

    payload = {
        "username": "MLB Model",
        "embeds": [
            {
                "title": f"⚾ MLB Model — {card['date']}",
                "description": card.get("description", "Confirmed plays and value watchlist."),
                "color": 0x2ECC71,
                "fields": fields,
                "footer": {"text": card.get("footer", "Confirm lineup and sportsbook price before betting.")},
            }
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    request = Request(
        webhook,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "MLB-Model/1.0"},
        method="POST",
    )
    with urlopen(request, timeout=20) as response:
        if response.status not in (200, 204):
            print(f"Discord returned HTTP {response.status}", file=sys.stderr)
            return 1
    print("Discord card posted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
