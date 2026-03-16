"""
OX Map Finder — Notion Database Setup
Creates a 'OX Standorte' database and adds 3 dummy entries.

Usage:
    export NOTION_API_KEY="secret_..."
    export NOTION_PARENT_PAGE_ID="your-page-id"
    python setup_notion_db.py
"""

import json
import os
import sys
import urllib.request

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "")
NOTION_VERSION = "2022-06-28"


def notion_request(method, endpoint, body=None):
    """Make a request to the Notion API."""
    url = f"https://api.notion.com/v1/{endpoint}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {NOTION_API_KEY}")
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def create_database():
    """Create the OX Standorte database."""
    print("Creating database 'OX Standorte'...")

    body = {
        "parent": {"type": "page_id", "page_id": PARENT_PAGE_ID},
        "icon": {"type": "emoji", "emoji": "📍"},
        "title": [{"type": "text", "text": {"content": "OX Standorte"}}],
        "properties": {
            "Name": {"title": {}},
            "Typ": {
                "select": {
                    "options": [
                        {"name": "Praxis", "color": "blue"},
                        {"name": "Klinik", "color": "green"},
                        {"name": "Arbeitgeber", "color": "orange"},
                    ]
                }
            },
            "Adresse": {"rich_text": {}},
            "Beschreibung": {"rich_text": {}},
            "Kontakt": {"email": {}},
        },
    }

    result = notion_request("POST", "databases", body)
    db_id = result["id"]
    print(f"Database created: {db_id}")
    return db_id


def add_entry(db_id, name, typ, adresse, beschreibung, kontakt):
    """Add a single entry to the database."""
    body = {
        "parent": {"database_id": db_id},
        "properties": {
            "Name": {"title": [{"text": {"content": name}}]},
            "Typ": {"select": {"name": typ}},
            "Adresse": {"rich_text": [{"text": {"content": adresse}}]},
            "Beschreibung": {"rich_text": [{"text": {"content": beschreibung}}]},
            "Kontakt": {"email": kontakt},
        },
    }
    notion_request("POST", "pages", body)
    print(f"  Added: {name}")


def main():
    if not NOTION_API_KEY or not PARENT_PAGE_ID:
        print("Error: Set NOTION_API_KEY and NOTION_PARENT_PAGE_ID environment variables.")
        print()
        print("  export NOTION_API_KEY='secret_...'")
        print("  export NOTION_PARENT_PAGE_ID='<page-id-from-notion-url>'")
        print()
        print("Make sure the parent page is shared with your integration!")
        sys.exit(1)

    db_id = create_database()

    print("\nAdding dummy entries...")
    entries = [
        {
            "name": "Physiotherapie Müller",
            "typ": "Praxis",
            "adresse": "Marienplatz 1, 80331 München",
            "beschreibung": "Zertifizierter OX Experte seit 2023",
            "kontakt": "info@physio-mueller.de",
        },
        {
            "name": "Rehazentrum am Park",
            "typ": "Klinik",
            "adresse": "Kurfürstendamm 42, 10719 Berlin",
            "beschreibung": "OX Partner-Klinik mit Schwerpunkt Orthopädie",
            "kontakt": "kontakt@reha-park.de",
        },
        {
            "name": "Bewegungslabor Stuttgart",
            "typ": "Arbeitgeber",
            "adresse": "Königstraße 28, 70173 Stuttgart",
            "beschreibung": "OX Partner — offene Stellen verfügbar",
            "kontakt": "karriere@bewegungslabor.de",
        },
    ]

    for entry in entries:
        add_entry(db_id, **entry)

    print(f"\nDone! Database ID: {db_id}")
    print(f"\nTo sync locations to the map, run:")
    print(f"  export NOTION_DATABASE_ID='{db_id}'")
    print(f"  python sync_notion.py")


if __name__ == "__main__":
    main()
