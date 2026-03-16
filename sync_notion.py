"""
OX Map Finder — Notion Sync Script
Pulls locations from a Notion database, geocodes addresses, and writes locations.json.

Usage:
    export NOTION_API_KEY="secret_..."
    export NOTION_DATABASE_ID="your-database-id"
    python sync_notion.py

Notion Database expected columns:
    - Name (title)
    - Typ (select: "Praxis", "Klinik", "Arbeitgeber")
    - Adresse (rich_text)
    - Beschreibung (rich_text)
    - Kontakt (email or rich_text)
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locations.json")


def notion_query(database_id, start_cursor=None):
    """Query all pages from a Notion database."""
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    body = {}
    if start_cursor:
        body["start_cursor"] = start_cursor

    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {NOTION_API_KEY}")
    req.add_header("Notion-Version", "2022-06-28")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_plain_text(prop):
    """Extract plain text from a Notion rich_text or title property."""
    if not prop:
        return ""
    prop_type = prop.get("type", "")
    items = prop.get(prop_type, []) if prop_type in ("rich_text", "title") else []
    return "".join(item.get("plain_text", "") for item in items)


def get_select(prop):
    """Extract value from a Notion select property."""
    if not prop or prop.get("type") != "select":
        return ""
    sel = prop.get("select")
    return sel.get("name", "") if sel else ""


def get_email(prop):
    """Extract email from a Notion email or rich_text property."""
    if not prop:
        return ""
    if prop.get("type") == "email":
        return prop.get("email", "") or ""
    return get_plain_text(prop)


def geocode(address):
    """Geocode an address using Nominatim (free, no API key)."""
    encoded = urllib.parse.urlencode({"q": address, "format": "json", "limit": 1})
    url = f"https://nominatim.openstreetmap.org/search?{encoded}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "OX-Map-Finder/1.0")

    try:
        with urllib.request.urlopen(req) as resp:
            results = json.loads(resp.read().decode("utf-8"))
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        print(f"  Geocoding failed for '{address}': {e}")
    return None, None


def sync():
    if not NOTION_API_KEY or not NOTION_DATABASE_ID:
        print("Error: Set NOTION_API_KEY and NOTION_DATABASE_ID environment variables.")
        sys.exit(1)

    print("Fetching locations from Notion...")
    locations = []
    has_more = True
    cursor = None

    while has_more:
        result = notion_query(NOTION_DATABASE_ID, cursor)
        for page in result.get("results", []):
            props = page.get("properties", {})

            name = get_plain_text(props.get("Name"))
            typ = get_select(props.get("Typ"))
            address = get_plain_text(props.get("Adresse"))
            description = get_plain_text(props.get("Beschreibung"))
            contact = get_email(props.get("Kontakt"))

            if not name or not address:
                print(f"  Skipping (missing name/address): {name or '(unnamed)'}")
                continue

            print(f"  Geocoding: {name} — {address}")
            lat, lng = geocode(address)
            if lat is None:
                print(f"  ⚠ Could not geocode, skipping: {address}")
                continue

            locations.append({
                "name": name,
                "type": typ or "Praxis",
                "address": address,
                "lat": lat,
                "lng": lng,
                "description": description,
                "contact": contact,
            })

            # Nominatim rate limit: 1 req/sec
            time.sleep(1.1)

        has_more = result.get("has_more", False)
        cursor = result.get("next_cursor")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(locations, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(locations)} locations written to {OUTPUT_FILE}")


if __name__ == "__main__":
    sync()
