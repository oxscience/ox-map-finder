# OX Map Finder

**Interactive location finder with Leaflet maps, Notion CMS, and Shopify integration.**

A dark-themed, responsive map application for finding practitioners, clinics, and employers. Locations are managed in Notion and synced via n8n webhooks.

## Features

- **Interactive Map**: Leaflet.js with custom colored markers (Praxis, Klinik, Arbeitgeber)
- **Sidebar Search**: Filter by type, search by name/city/ZIP
- **Notion as CMS**: Manage locations in a Notion database — no code needed to add/edit
- **n8n Sync**: Webhook-based sync from Notion to JSON with geocoding
- **Shopify Embeddable**: Liquid section template for embedding in any Shopify store
- **iframe Mode**: Auto-detects embedding and hides branding
- **Dark Mode**: Full dark theme with CARTO Voyager map tiles
- **Responsive**: Sidebar + map on desktop, stacked layout on mobile

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vanilla HTML/CSS/JS |
| Map | Leaflet.js + CARTO tiles |
| CMS | Notion API |
| Automation | n8n workflow |
| Embedding | Shopify Liquid templates |
| Data | JSON (synced from Notion) |

## Quick Start

Just open `index.html` in a browser, or serve it:

```bash
python -m http.server 8000
```

### Notion Setup

```bash
pip install -r requirements.txt
python setup_notion_db.py  # Creates the Notion database
python sync_notion.py      # Syncs locations to locations.json
```

### Shopify Integration

Copy the files from `shopify/` into your theme:

- `sections/ox-map-finder.liquid` → Theme sections
- `templates/page.ox-map.json` → Page template

## License

MIT
