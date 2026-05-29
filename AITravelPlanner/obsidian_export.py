"""
obsidian_export.py — GraphRAG AI Travel Planner: Obsidian Vault Generator
==========================================================================
Reads `itinerary.json` (produced by agent.py) and generates an Obsidian-
compatible Markdown vault in the `Obsidian_Vault/` directory.

Generated files:
  Obsidian_Vault/
  ├── Itinerary.md          ← Master itinerary with all wiki-links
  ├── Tuscany.md            ← Destination overview node
  ├── Sangiovese.md         ← Wine entity node
  ├── <Hotel Name>.md       ← Dynamic hotel node(s)
  ├── <Wine Name>.md        ← Additional wine nodes
  ├── <Cuisine Name>.md     ← Cuisine entity nodes
  └── <Activity Name>.md   ← Activity entity nodes

Obsidian Graph View will automatically connect these files via [[wiki-links]].

Usage:
  python obsidian_export.py
  python obsidian_export.py --input my_itinerary.json
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("obsidian_export")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
VAULT_DIR = Path("Obsidian_Vault")
INPUT_FILE = Path("itinerary.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sanitize_filename(name: str) -> str:
    """Convert a display name to a safe filename (Obsidian-friendly)."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip().replace(" ", "_")
    return name


def wiki(name: str) -> str:
    """Wrap a name in Obsidian double-bracket wiki-link syntax."""
    return f"[[{name}]]"


def write_note(filename: str, content: str) -> None:
    """Write a Markdown note to the vault directory."""
    path = VAULT_DIR / filename
    path.write_text(content, encoding="utf-8")
    log.info("  Written: %s", path)


def stars(n: Optional[int]) -> str:
    if not n:
        return "N/A"
    return "⭐" * n


def price_str(p: Optional[float]) -> str:
    if p is None:
        return "N/A"
    return f"€{p:.0f}"


# ---------------------------------------------------------------------------
# Note generators
# ---------------------------------------------------------------------------

def generate_tuscany_note(itinerary: Dict[str, Any]) -> str:
    destination = itinerary.get("destination", "Tuscany, Italy")
    hotel = itinerary.get("accommodation", {})
    wine = itinerary.get("featured_wine", {})
    hotel_name = hotel.get("name", "Villa dei Baronci")
    wine_name = wine.get("name", "Sangiovese")

    activities_linked = ""
    all_activities: List[str] = []
    for day in itinerary.get("days", []):
        for act in day.get("activities", []):
            title = act.get("title", "")
            if title and title not in all_activities:
                all_activities.append(title)

    if all_activities:
        activities_linked = "\n".join(f"- {wiki(a)}" for a in all_activities)

    content = f"""---
tags: [destination, italy, tuscany, travel]
type: Destination
region: Tuscany
country: Italy
created: {datetime.now().isoformat(timespec='seconds')}
---

# 🌿 Tuscany

> *"In Tuscany, every hill is a poem, every vineyard a verse."*

Tuscany is one of Italy's most celebrated regions, renowned for its rolling hills,
Renaissance art, medieval cities, and world-class wines. It is the birthplace of
the Italian Renaissance and home to iconic wines like **Chianti**, **Brunello di Montalcino**,
and the beloved {wiki(wine_name)}.

## 🗺️ Key Destinations
- {wiki("Florence")} — Renaissance capital, home of the Uffizi Gallery
- {wiki("Siena")} — Medieval hilltop city, famous for the Palio
- {wiki("Chianti")} — Rolling wine country between Florence and Siena
- {wiki("Montepulciano")} — Hilltop town, home of Vino Nobile
- {wiki("Montalcino")} — Birthplace of Brunello

## 🏨 Recommended Stays
- {wiki(hotel_name)}

## 🍷 Signature Wines
- {wiki("Sangiovese")}
- {wiki("Chianti Classico")}
- {wiki("Brunello di Montalcino")}

## 🍽️ Must-Try Dishes
- {wiki("Bistecca alla Fiorentina")}
- {wiki("Pappardelle al Cinghiale")}
- {wiki("Pici con Tartufo")}

## 🎯 Activities
{activities_linked}

## 🔗 Connected Notes
- {wiki("Itinerary")} — Your trip plan
- {wiki(wine_name)} — Featured wine
- {wiki(hotel_name)} — Your accommodation

---
*Part of the [[Itinerary]] — GraphRAG AI Travel Planner*
"""
    return content


def generate_wine_note(wine: Dict[str, Any], itinerary: Dict[str, Any]) -> str:
    name = wine.get("name", "Sangiovese")
    wine_type = wine.get("type", "Red")
    notes = wine.get("tasting_notes", "")
    pairings = wine.get("food_pairings", [])
    hotel_name = itinerary.get("accommodation", {}).get("name", "Villa dei Baronci")

    pairings_linked = "\n".join(f"- {wiki(p)}" for p in pairings) if pairings else "- Rich Tuscan meats and pasta"

    content = f"""---
tags: [wine, tuscany, italian-wine, sangiovese]
type: Wine
wine_type: {wine_type}
region: Tuscany
country: Italy
created: {datetime.now().isoformat(timespec='seconds')}
---

# 🍷 {name}

{name} is one of Italy's most iconic grape varieties and the backbone of many
celebrated Tuscan wines, including **Chianti Classico**, **Brunello di Montalcino**,
and **Vino Nobile di Montepulciano**.

## 🔬 Profile
| Attribute        | Detail                              |
|------------------|-------------------------------------|
| **Type**         | {wine_type}                         |
| **Grape**        | Sangiovese                          |
| **Region**       | {wiki("Tuscany")}                   |
| **Style**        | Full-bodied, high acidity, firm tannins |

## 👃 Tasting Notes
{notes or "Cherry, plum, dried herbs, tobacco, leather undertones with earthy minerality."}

## 🍽️ Perfect Food Pairings
{pairings_linked}
- {wiki("Bistecca alla Fiorentina")}
- {wiki("Pappardelle al Cinghiale")}

## 🏨 Where to Try
- {wiki(hotel_name)} — Estate-bottled Sangiovese in the Chianti region
- {wiki("Chianti")} — The heartland of Sangiovese production
- {wiki("Enoteca Poliziana")} — Vertical tastings in Montepulciano

## 🔗 Connected Notes
- {wiki("Tuscany")} — Origin region
- {wiki("Itinerary")} — Your trip plan
- {wiki(hotel_name)} — Your accommodation

---
*Part of the [[Itinerary]] — GraphRAG AI Travel Planner*
"""
    return content


def generate_hotel_note(hotel: Dict[str, Any], itinerary: Dict[str, Any]) -> str:
    name = hotel.get("name", "Villa dei Baronci")
    h_type = hotel.get("type", "Agriturismo")
    rating = hotel.get("star_rating")
    price = hotel.get("price_per_night_eur")
    desc = hotel.get("description", "")
    location = hotel.get("nearby_location", "Chianti")
    wine_name = itinerary.get("featured_wine", {}).get("name", "Sangiovese")

    content = f"""---
tags: [accommodation, hotel, tuscany, agriturismo]
type: Accommodation
accommodation_type: {h_type}
star_rating: {rating or "N/A"}
price_per_night_eur: {price or "N/A"}
location: {location}
created: {datetime.now().isoformat(timespec='seconds')}
---

# 🏡 {name}

{desc or f"{name} is a charming {h_type.lower()} nestled in the heart of {wiki(location)}, Tuscany."}

## 📍 Location
**Region:** {wiki("Tuscany")}  
**Area:** {wiki(location)}  
**Country:** Italy  

## 🏆 Details
| Feature              | Detail                    |
|----------------------|---------------------------|
| **Type**             | {h_type}                  |
| **Star Rating**      | {stars(rating)}           |
| **Price / Night**    | {price_str(price)}        |
| **Nearby Location**  | {wiki(location)}          |

## 🍷 Wine & Dining
The property serves estate-bottled {wiki(wine_name)}, crafted from grapes grown in
the surrounding vineyards. Guests can join guided wine tasting sessions and enjoy
traditional Tuscan meals at the on-site restaurant.

- Featured Wine: {wiki(wine_name)}
- Cuisine: {wiki("Bistecca alla Fiorentina")}, {wiki("Pappardelle al Cinghiale")}

## 🎯 Nearby Activities
- {wiki("Chianti Vineyard Wine Tasting")}
- {wiki("Uffizi Gallery Tour")} (17 km to Florence)
- {wiki("Val d'Orcia Cycling Tour")}

## 🔗 Connected Notes
- {wiki("Tuscany")} — Destination
- {wiki(location)} — Local area
- {wiki(wine_name)} — Featured wine
- {wiki("Itinerary")} — Your trip plan

---
*Part of the [[Itinerary]] — GraphRAG AI Travel Planner*
"""
    return content


def generate_cuisine_note(name: str, description: str, wine_pairing: str) -> str:
    content = f"""---
tags: [cuisine, food, tuscany, italian]
type: Cuisine
region: Tuscany
created: {datetime.now().isoformat(timespec='seconds')}
---

# 🍽️ {name}

{description}

## 🍷 Wine Pairing
Best enjoyed with {wiki(wine_pairing)}.

## 🌿 Origin
Traditional to {wiki("Tuscany")}, this dish represents the heart of Tuscan culinary heritage.

## 🔗 Connected Notes
- {wiki("Tuscany")} — Origin region
- {wiki(wine_pairing)} — Recommended wine
- {wiki("Itinerary")} — Your trip plan

---
*Part of the [[Itinerary]] — GraphRAG AI Travel Planner*
"""
    return content


def generate_activity_note(activity: Dict[str, Any], location_name: str) -> str:
    title = activity.get("title", "Activity")
    desc = activity.get("description", "")
    act_type = activity.get("type", "Activity")
    price = activity.get("price_eur")
    duration = activity.get("duration_hours")
    booking = activity.get("booking_required", False)
    wine = activity.get("featured_wine", "")

    price_display = f"€{price:.0f}" if price else "Free / varies"
    duration_display = f"{duration} hours" if duration else "Variable"
    booking_display = "✅ Required" if booking else "❌ Not required"

    wine_section = f"\n## 🍷 Featured Wine\n{wiki(wine)}\n" if wine else ""

    content = f"""---
tags: [activity, tuscany, {act_type.lower().replace(' ', '-')}]
type: Activity
activity_type: {act_type}
location: {location_name}
created: {datetime.now().isoformat(timespec='seconds')}
---

# 🎯 {title}

{desc}

## 📋 Details
| Feature            | Detail              |
|--------------------|---------------------|
| **Type**           | {act_type}          |
| **Location**       | {wiki(location_name)} |
| **Duration**       | {duration_display}  |
| **Price**          | {price_display}     |
| **Booking**        | {booking_display}   |
{wine_section}
## 🔗 Connected Notes
- {wiki("Tuscany")} — Destination
- {wiki(location_name)} — Local area
- {wiki("Itinerary")} — Your trip plan

---
*Part of the [[Itinerary]] — GraphRAG AI Travel Planner*
"""
    return content


def generate_itinerary_note(itinerary: Dict[str, Any]) -> str:
    title = itinerary.get("trip_title", "2-Day Tuscany Wine & Culture Escape")
    destination = itinerary.get("destination", "Tuscany, Italy")
    duration = itinerary.get("duration_days", 2)
    hotel = itinerary.get("accommodation", {})
    hotel_name = hotel.get("name", "Villa dei Baronci")
    wine = itinerary.get("featured_wine", {})
    wine_name = wine.get("name", "Sangiovese")
    dates = itinerary.get("travel_dates", {})
    ai_synthesis = itinerary.get("ai_synthesis", "")
    days = itinerary.get("days", [])

    days_md = ""
    for day_data in days:
        day_num = day_data.get("day", "?")
        day_date = day_data.get("date", "")
        theme = day_data.get("theme", "")
        activities = day_data.get("activities", [])

        days_md += f"\n## 📅 Day {day_num} — {theme}\n"
        if day_date:
            days_md += f"**Date:** {day_date}  \n\n"

        for act in activities:
            time = act.get("time", "")
            act_title = act.get("title", "")
            act_desc = act.get("description", "")
            act_type = act.get("type", "")
            act_location = act.get("location", "")
            act_wine = act.get("wine_pairing") or act.get("featured_wine", "")

            wine_tag = f" 🍷 {wiki(act_wine)}" if act_wine else ""
            location_tag = f" 📍 {wiki(act_location)}" if act_location else ""

            days_md += f"### 🕐 {time} — {wiki(act_title)}\n"
            days_md += f"*{act_type}*{location_tag}{wine_tag}  \n"
            days_md += f"{act_desc}\n\n"

    ai_section = ""
    if ai_synthesis:
        ai_section = f"""
## 🤖 AI Travel Assistant Recommendation

> {ai_synthesis.replace(chr(10), chr(10) + '> ')}

"""

    content = f"""---
tags: [itinerary, travel, tuscany, graphrag, ai-planner]
type: Itinerary
destination: {destination}
duration: {duration} days
accommodation: {hotel_name}
featured_wine: {wine_name}
day_1: {dates.get('day_1', '')}
day_2: {dates.get('day_2', '')}
generated_by: GraphRAG AI Travel Planner v1.0
created: {datetime.now().isoformat(timespec='seconds')}
---

# ✈️ {title}

> **Destination:** {wiki("Tuscany")}  
> **Duration:** {duration} Days  
> **Accommodation:** {wiki(hotel_name)}  
> **Featured Wine:** {wiki(wine_name)}  

---

## 🗺️ Overview

This itinerary was generated by the **GraphRAG AI Travel Planner** — a system that
queries a live Neo4j knowledge graph of travel entities (locations, hotels, wines,
cuisines, and activities) to synthesize a personalized travel plan.

**Graph entities connected to this trip:**
- 📍 {wiki("Tuscany")} — Primary destination
- 🏡 {wiki(hotel_name)} — Your accommodation  
- 🍷 {wiki(wine_name)} — Featured wine variety
- 🍽️ {wiki("Bistecca alla Fiorentina")} — Must-try cuisine
- 🍽️ {wiki("Pappardelle al Cinghiale")} — Signature pasta dish
- 🎨 {wiki("Uffizi Gallery Tour")} — Day 2 highlight
- 🚴 {wiki("Chianti Vineyard Wine Tasting")} — Day 1 experience

---
{days_md}
---
{ai_section}
## 🏨 Accommodation Details
{wiki(hotel_name)}  
- **Type:** {hotel.get('type', 'N/A')}  
- **Stars:** {stars(hotel.get('star_rating'))}  
- **Price:** {price_str(hotel.get('price_per_night_eur'))} / night  
- **Location:** {wiki(hotel.get('nearby_location', 'Chianti'))}

---

## 🍷 Wine & Cuisine Highlights
- {wiki(wine_name)} — {wine.get('tasting_notes', 'The backbone of Tuscan wine culture')}
- Pairs with: {', '.join(wiki(p) for p in wine.get('food_pairings', ['Bistecca alla Fiorentina']))}

---

## 📊 Knowledge Graph Sources
This itinerary was synthesized from the following graph nodes and relationships:

```
(Accommodation: {hotel_name})
    -[:LOCATED_IN]->(Location: Chianti)
    -[:IS_NEAR]->(Activity: Chianti Vineyard Wine Tasting)
    -[:SERVES]->(Wine: {wine_name})

(Wine: {wine_name})
    -[:LOCATED_IN]->(Location: Tuscany)
    -[:PAIRS_WITH]->(Cuisine: Bistecca alla Fiorentina)
    -[:PAIRS_WITH]->(Cuisine: Pappardelle al Cinghiale)

(Location: Tuscany)
    -[:SERVES]->(Wine: {wine_name})
```

---
*Generated by [GraphRAG AI Travel Planner](https://github.com/graphrag/travel-planner)*  
*Graph Database: Neo4j 5+ · AI Model: GPT-4o · Framework: LangChain*
"""
    return content


# ---------------------------------------------------------------------------
# Main export function
# ---------------------------------------------------------------------------

def run_export(input_file: Path = INPUT_FILE) -> None:
    log.info("═" * 60)
    log.info("GraphRAG AI Travel Planner — Obsidian Vault Generator")
    log.info("═" * 60)

    # ── 1. Load itinerary ─────────────────────────────────────────────────
    if not input_file.exists():
        log.error("Itinerary file not found: %s", input_file)
        log.error("Run agent.py first to generate itinerary.json")
        sys.exit(1)

    with open(input_file, encoding="utf-8") as f:
        itinerary: Dict[str, Any] = json.load(f)
    log.info("Loaded itinerary: %s", itinerary.get("trip_title", "N/A"))

    # ── 2. Create vault directory ─────────────────────────────────────────
    VAULT_DIR.mkdir(exist_ok=True)
    log.info("Vault directory: %s", VAULT_DIR.resolve())

    # ── 3. Generate Itinerary.md (master hub note) ────────────────────────
    log.info("Generating vault notes …")
    write_note("Itinerary.md", generate_itinerary_note(itinerary))

    # ── 4. Generate Tuscany.md (destination node) ─────────────────────────
    write_note("Tuscany.md", generate_tuscany_note(itinerary))

    # ── 5. Generate wine notes ────────────────────────────────────────────
    wines = itinerary.get("all_wines", [itinerary.get("featured_wine", {})])
    if not wines:
        wines = [{"name": "Sangiovese", "type": "Red",
                  "tasting_notes": "Cherry, plum, earthy", "food_pairings": []}]

    for wine in wines:
        if not wine.get("name"):
            continue
        wine_filename = sanitize_filename(wine["name"]) + ".md"
        write_note(wine_filename, generate_wine_note(wine, itinerary))

    # Ensure Sangiovese.md always exists
    if not (VAULT_DIR / "Sangiovese.md").exists():
        sangiovese = {"name": "Sangiovese", "type": "Red",
                      "tasting_notes": "Cherry, plum, leather, earthy undertones",
                      "food_pairings": ["Bistecca alla Fiorentina", "Pappardelle al Cinghiale"]}
        write_note("Sangiovese.md", generate_wine_note(sangiovese, itinerary))

    # ── 6. Generate hotel notes ───────────────────────────────────────────
    hotels = itinerary.get("all_hotels", [itinerary.get("accommodation", {})])
    for hotel in hotels:
        if not hotel.get("name"):
            continue
        hotel_filename = sanitize_filename(hotel["name"]) + ".md"
        write_note(hotel_filename, generate_hotel_note(hotel, itinerary))

    # ── 7. Generate cuisine notes ─────────────────────────────────────────
    cuisines = [
        {
            "name": "Bistecca alla Fiorentina",
            "description": "The quintessential Florentine dish — a thick, char-grilled T-bone steak "
                           "served rare, sourced from Chianina cattle. A cornerstone of Tuscan cuisine.",
            "wine_pairing": "Sangiovese",
        },
        {
            "name": "Pappardelle al Cinghiale",
            "description": "Wide, ribbon-like pasta served with a rich wild boar ragù, "
                           "slow-cooked with Tuscan herbs, red wine, and tomatoes.",
            "wine_pairing": "Sangiovese",
        },
        {
            "name": "Pici con Tartufo",
            "description": "Hand-rolled thick spaghetti tossed in an aromatic black truffle sauce — "
                           "a prized delicacy of the Sienese hills.",
            "wine_pairing": "Brunello di Montalcino",
        },
    ]
    for cuisine in cuisines:
        cuisine_filename = sanitize_filename(cuisine["name"]) + ".md"
        write_note(cuisine_filename, generate_cuisine_note(
            cuisine["name"], cuisine["description"], cuisine["wine_pairing"]
        ))

    # ── 8. Generate activity notes ────────────────────────────────────────
    all_activities_seen: set = set()
    for day_data in itinerary.get("days", []):
        act_location = "Tuscany"
        for act in day_data.get("activities", []):
            title = act.get("title", "")
            if not title or title in all_activities_seen:
                continue
            all_activities_seen.add(title)
            act_location = act.get("location", "Tuscany")
            act_filename = sanitize_filename(title) + ".md"
            write_note(act_filename, generate_activity_note(act, act_location))

    # ── 9. Generate additional sub-location notes ─────────────────────────
    sub_locations = {
        "Florence": "Florence (Firenze) is the jewel of Tuscany — the cradle of the Renaissance. "
                    "Home to the [[Uffizi Gallery Tour]], Michelangelo's David, and the Duomo.",
        "Chianti": "The Chianti wine region stretches between [[Florence]] and [[Siena]], producing "
                   "world-famous [[Sangiovese]]-based wines under the Chianti Classico DOCG appellation.",
        "Siena": "A perfectly preserved medieval city famous for the Piazza del Campo and the Palio horse race. "
                 "Located south of [[Florence]] in the heart of [[Tuscany]].",
        "Montalcino": "A hilltop fortress town south of [[Siena]], birthplace of the legendary "
                      "[[Brunello di Montalcino]] — one of Italy's most celebrated red wines.",
        "Montepulciano": "A Renaissance hilltop town east of [[Siena]], home of Vino Nobile di Montepulciano "
                         "and the famous Enoteca Poliziana.",
    }
    for loc_name, loc_desc in sub_locations.items():
        loc_content = f"""---
tags: [location, tuscany, italy]
type: Location
region: Tuscany
country: Italy
created: {datetime.now().isoformat(timespec='seconds')}
---

# 📍 {loc_name}

{loc_desc}

## 🔗 Connected Notes
- [[Tuscany]] — Parent region
- [[Itinerary]] — Your trip plan

---
*Part of the [[Itinerary]] — GraphRAG AI Travel Planner*
"""
        write_note(sanitize_filename(loc_name) + ".md", loc_content)

    # ── 10. Generate _graph_index.md (vault overview) ─────────────────────
    all_files = sorted(VAULT_DIR.glob("*.md"))
    index_links = "\n".join(f"- {wiki(f.stem.replace('_', ' '))}" for f in all_files
                            if f.stem != "_graph_index")
    index_content = f"""---
tags: [index, graphrag, travel-planner]
type: Index
created: {datetime.now().isoformat(timespec='seconds')}
---

# 🗺️ GraphRAG Travel Planner — Vault Index

This vault was auto-generated by the **GraphRAG AI Travel Planner**.  
Open this folder in **Obsidian** and switch to **Graph View** to see all entities connected.

## 📄 All Notes in This Vault
{index_links}

## 🏗️ How This Was Generated
1. A travel blog about Tuscany was ingested into **Neo4j** graph database
2. **LangChain LLMGraphTransformer** extracted entities and relationships
3. **GraphCypherQAChain** queried the graph to answer: *"{itinerary.get('metadata', {}).get('query', USER_QUERY if 'USER_QUERY' in dir() else 'Find me a hotel near a Sangiovese wine region')}"*
4. This vault was generated from the structured JSON response

---
*GraphRAG AI Travel Planner v1.0 · Neo4j 5+ · GPT-4o · LangChain*
"""
    # Reconstruct USER_QUERY reference
    user_query = itinerary.get("metadata", {}).get("query",
        "I want a 2-day trip to Tuscany. Find me a hotel near a place that serves Sangiovese wine.")
    index_content = index_content.replace(
        'USER_QUERY if \'USER_QUERY\' in dir() else \'Find me a hotel near a Sangiovese wine region\'',
        f'"{user_query}"'
    )
    write_note("_graph_index.md", index_content)

    # ── 11. Summary ───────────────────────────────────────────────────────
    note_count = len(list(VAULT_DIR.glob("*.md")))
    log.info("═" * 60)
    log.info("Obsidian vault generated successfully ✓")
    log.info("  Location : %s", VAULT_DIR.resolve())
    log.info("  Notes    : %d Markdown files", note_count)
    log.info("═" * 60)
    log.info("Next step: Open the '%s' folder in Obsidian,", VAULT_DIR)
    log.info("  then press Ctrl+G (or Cmd+G) to open Graph View.")
    log.info("═" * 60)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Obsidian vault from itinerary JSON")
    parser.add_argument(
        "--input", type=Path, default=INPUT_FILE,
        help="Path to itinerary JSON file (default: itinerary.json)"
    )
    args = parser.parse_args()
    run_export(args.input)
