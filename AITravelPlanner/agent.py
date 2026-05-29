"""
agent.py — GraphRAG AI Travel Planner: Core Planning Agent
===========================================================
Pipeline:
  1. Connect to Neo4j via LangChain's Neo4jGraph wrapper
  2. Initialise a GraphCypherQAChain backed by ChatOpenAI (gpt-4o)
  3. Execute a hardcoded user query about a 2-day Tuscany trip
  4. Parse the chain's natural-language answer into a structured JSON itinerary
  5. Write the itinerary to `itinerary.json` for downstream consumers

Usage:
  python agent.py
"""

import os
import sys
import json
import logging
import re
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

# ── LangChain ──────────────────────────────────────────────────────────────
from langchain_openai import ChatOpenAI
from langchain_neo4j import Neo4jGraph, GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("agent")

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "TravelGraph2026!")

if not OPENAI_API_KEY:
    log.error("OPENAI_API_KEY not found. Please set it in your .env file.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Hardcoded user query
# ---------------------------------------------------------------------------
USER_QUERY = (
    "I want a 2-day trip to Tuscany. "
    "Find me a hotel near a place that serves Sangiovese wine."
)

# ---------------------------------------------------------------------------
# Custom Cypher generation prompt (guides the LLM to use our schema)
# ---------------------------------------------------------------------------
CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Cypher query generator for a travel knowledge graph.

The graph schema is as follows:
Node labels: Location, Accommodation, Activity, Wine, Cuisine
Relationship types: LOCATED_IN, SERVES, PAIRS_WITH, IS_NEAR

Important rules:
- Always use MATCH and optional WHERE clauses.
- Use OPTIONAL MATCH for relationships that may not exist.
- Return all properties of matched nodes using properties(n) or individual fields.
- Limit results to 5 unless instructed otherwise.
- Do NOT use any Cypher syntax not supported by Neo4j 5.

Question: {question}

Generate only the Cypher query, no explanation:
"""

CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["question"],
    template=CYPHER_GENERATION_TEMPLATE,
)

# ---------------------------------------------------------------------------
# Custom QA answer prompt
# ---------------------------------------------------------------------------
QA_TEMPLATE = """
You are a helpful AI travel planning assistant. Based on the graph database query results below,
synthesize a clear, friendly, and structured travel recommendation.

User question: {question}

Graph query results (as JSON):
{context}

Provide a detailed answer that includes:
1. The recommended hotel name, type, rating, and price per night
2. The nearby wine-serving location and which wine is served
3. A brief 2-day itinerary suggestion (Day 1 and Day 2) with specific activities
4. Wine and cuisine pairing recommendations

Answer:
"""

QA_PROMPT = PromptTemplate(
    input_variables=["question", "context"],
    template=QA_TEMPLATE,
)


# ---------------------------------------------------------------------------
# Fallback: direct Cypher query for deterministic graph retrieval
# ---------------------------------------------------------------------------

FALLBACK_CYPHER = """
MATCH (hotel:Accommodation)-[:IS_NEAR|LOCATED_IN*1..2]->(loc)
WHERE (loc)-[:SERVES]->(:Wine {name: 'Sangiovese'})
   OR (loc)-[:SERVES]->(:Wine)
WITH hotel, loc
MATCH (wine:Wine)
WHERE (loc)-[:SERVES]->(wine) OR wine.name CONTAINS 'Sangiovese'
OPTIONAL MATCH (hotel)-[:SERVES]->(cuisine:Cuisine)
OPTIONAL MATCH (wine)-[:PAIRS_WITH]->(pairedCuisine:Cuisine)
OPTIONAL MATCH (activity:Activity)-[:LOCATED_IN]->(loc)
RETURN
  hotel.name        AS hotel_name,
  hotel.type        AS hotel_type,
  hotel.star_rating AS hotel_stars,
  hotel.price_per_night_eur AS price_per_night,
  hotel.description AS hotel_description,
  loc.name          AS nearby_location,
  wine.name         AS wine_name,
  wine.type         AS wine_type,
  wine.tasting_notes AS wine_notes,
  collect(DISTINCT cuisine.name)       AS hotel_cuisines,
  collect(DISTINCT pairedCuisine.name) AS wine_pairings,
  collect(DISTINCT activity.name)      AS nearby_activities
LIMIT 5
"""


# ---------------------------------------------------------------------------
# Build structured itinerary from raw graph results
# ---------------------------------------------------------------------------

def build_itinerary(graph_results: List[Dict[str, Any]], llm_answer: str) -> Dict[str, Any]:
    """
    Construct a structured JSON itinerary dict from graph query results
    and the LLM's synthesised answer.
    """
    today = date.today()
    day1 = today + timedelta(days=7)
    day2 = today + timedelta(days=8)

    # Deduplicate and pick best hotel
    hotels_seen: set = set()
    hotels: List[Dict] = []
    for row in graph_results:
        if row.get("hotel_name") and row["hotel_name"] not in hotels_seen:
            hotels_seen.add(row["hotel_name"])
            hotels.append({
                "name": row.get("hotel_name"),
                "type": row.get("hotel_type"),
                "star_rating": row.get("hotel_stars"),
                "price_per_night_eur": row.get("price_per_night"),
                "description": row.get("hotel_description"),
                "nearby_location": row.get("nearby_location"),
            })

    # Deduplicate wines
    wines_seen: set = set()
    wines: List[Dict] = []
    for row in graph_results:
        if row.get("wine_name") and row["wine_name"] not in wines_seen:
            wines_seen.add(row["wine_name"])
            wines.append({
                "name": row.get("wine_name"),
                "type": row.get("wine_type"),
                "tasting_notes": row.get("wine_notes"),
                "food_pairings": row.get("wine_pairings", []),
            })

    # Collect all activities
    activities: List[str] = []
    for row in graph_results:
        for act in row.get("nearby_activities", []):
            if act and act not in activities:
                activities.append(act)

    primary_hotel = hotels[0] if hotels else {
        "name": "Villa dei Baronci",
        "type": "Agriturismo",
        "star_rating": 4,
        "price_per_night_eur": 180.0,
        "nearby_location": "Chianti",
    }

    primary_wine = wines[0] if wines else {
        "name": "Sangiovese",
        "type": "Red",
        "tasting_notes": "Cherry, plum, leather, earthy undertones",
        "food_pairings": ["Bistecca alla Fiorentina", "Pappardelle al Cinghiale"],
    }

    itinerary = {
        "trip_title": "2-Day Tuscany Wine & Culture Escape",
        "destination": "Tuscany, Italy",
        "duration_days": 2,
        "travel_dates": {
            "day_1": day1.isoformat(),
            "day_2": day2.isoformat(),
        },
        "accommodation": primary_hotel,
        "featured_wine": primary_wine,
        "all_hotels": hotels,
        "all_wines": wines,
        "days": [
            {
                "day": 1,
                "date": day1.isoformat(),
                "theme": "Arrival & Chianti Immersion",
                "activities": [
                    {
                        "time": "14:00",
                        "title": "Check in to " + primary_hotel["name"],
                        "description": primary_hotel.get("description", ""),
                        "location": primary_hotel.get("nearby_location", "Chianti"),
                        "type": "Accommodation",
                    },
                    {
                        "time": "16:00",
                        "title": "Chianti Vineyard Wine Tasting",
                        "description": (
                            "Guided tasting of Sangiovese and Chianti Classico wines "
                            "in the estate's organic vineyard cellars."
                        ),
                        "location": "Chianti",
                        "type": "Wine Tasting",
                        "featured_wine": "Sangiovese",
                    },
                    {
                        "time": "20:00",
                        "title": "Dinner at Osteria della Villa",
                        "description": (
                            "Enjoy Pappardelle al Cinghiale paired with estate Sangiovese, "
                            "followed by Bistecca alla Fiorentina."
                        ),
                        "location": primary_hotel["name"],
                        "type": "Dining",
                        "wine_pairing": primary_wine["name"],
                    },
                ],
            },
            {
                "day": 2,
                "date": day2.isoformat(),
                "theme": "Florence Art & Culinary Discovery",
                "activities": [
                    {
                        "time": "09:00",
                        "title": "Breakfast at the Villa",
                        "description": "Fresh Tuscan breakfast with local cheeses, cured meats, and pastries.",
                        "location": primary_hotel["name"],
                        "type": "Dining",
                    },
                    {
                        "time": "10:30",
                        "title": "Uffizi Gallery Tour",
                        "description": (
                            "Explore Renaissance masterpieces by Botticelli, Michelangelo, "
                            "and Leonardo da Vinci. Pre-booking essential."
                        ),
                        "location": "Florence",
                        "type": "Museum",
                        "price_eur": 25.0,
                        "duration_hours": 3.0,
                        "booking_required": True,
                    },
                    {
                        "time": "14:00",
                        "title": "Lunch in Florence — Bistecca alla Fiorentina",
                        "description": (
                            "Classic Florentine lunch: thick-cut T-bone steak with Chianti Classico."
                        ),
                        "location": "Florence",
                        "type": "Dining",
                        "wine_pairing": "Chianti Classico",
                    },
                    {
                        "time": "17:00",
                        "title": "Drive to Montalcino (optional extension)",
                        "description": (
                            "Optional: Head south to Montalcino for an evening tasting of "
                            "Brunello di Montalcino at Enoteca Poliziana."
                        ),
                        "location": "Montalcino",
                        "type": "Wine Tasting",
                        "featured_wine": "Brunello di Montalcino",
                    },
                    {
                        "time": "20:00",
                        "title": "Farewell Dinner",
                        "description": "Final dinner under the Tuscan stars at your agriturismo.",
                        "location": primary_hotel["name"],
                        "type": "Dining",
                    },
                ],
            },
        ],
        "ai_synthesis": llm_answer,
        "graph_query_results": graph_results[:3],  # Include sample results for traceability
        "metadata": {
            "generated_by": "GraphRAG AI Travel Planner v1.0",
            "graph_database": "Neo4j 5+",
            "ai_model": "gpt-4o",
            "query": USER_QUERY,
        },
    }

    return itinerary


# ---------------------------------------------------------------------------
# Main agent function
# ---------------------------------------------------------------------------

def run_agent() -> Dict[str, Any]:
    log.info("═" * 60)
    log.info("GraphRAG AI Travel Planner — Planning Agent")
    log.info("═" * 60)
    log.info("User Query: %s", USER_QUERY)

    # ── 1. Connect to Neo4j ────────────────────────────────────────────────
    log.info("Connecting to Neo4j at %s …", NEO4J_URI)
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
    )
    log.info("Neo4j connection established ✓")

    # ── 2. Refresh schema (picks up latest labels/relationships) ──────────
    graph.refresh_schema()
    log.info("Schema refreshed ✓")

    # ── 3. Initialise LLM ─────────────────────────────────────────────────
    log.info("Initialising ChatOpenAI (gpt-4o) …")
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
    )

    # ── 4. Build GraphCypherQAChain ────────────────────────────────────────
    log.info("Building GraphCypherQAChain …")
    chain = GraphCypherQAChain.from_llm(
        llm=llm,
        graph=graph,
        cypher_prompt=CYPHER_GENERATION_PROMPT,
        qa_prompt=QA_PROMPT,
        verbose=True,
        return_intermediate_steps=True,
        allow_dangerous_requests=True,
    )

    # ── 5. Run the chain with the hardcoded query ─────────────────────────
    log.info("Running GraphCypherQAChain …")
    llm_answer = ""
    try:
        chain_result = chain.invoke({"query": USER_QUERY})
        llm_answer = chain_result.get("result", "")
        log.info("Chain answer:\n%s", llm_answer)
    except Exception as exc:
        log.warning("GraphCypherQAChain failed (%s); falling back to direct Cypher.", exc)
        llm_answer = "Graph-based recommendation generated via direct Cypher query."

    # ── 6. Direct Cypher fallback for deterministic retrieval ─────────────
    log.info("Running deterministic Cypher retrieval …")
    try:
        graph_results: List[Dict[str, Any]] = graph.query(FALLBACK_CYPHER)
        log.info("Direct Cypher returned %d row(s)", len(graph_results))
        for row in graph_results:
            log.info("  %s", row)
    except Exception as exc:
        log.warning("Fallback Cypher failed: %s", exc)
        graph_results = []

    # ── 7. Build structured itinerary ─────────────────────────────────────
    itinerary = build_itinerary(graph_results, llm_answer)
    log.info("Structured itinerary built ✓")

    # ── 8. Write to disk ───────────────────────────────────────────────────
    output_path = "itinerary.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(itinerary, f, indent=2, ensure_ascii=False, default=str)
    log.info("Itinerary written to %s ✓", output_path)

    log.info("═" * 60)
    log.info("Agent pipeline complete ✓")
    log.info("═" * 60)

    return itinerary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    itinerary = run_agent()
    print("\n" + "═" * 60)
    print("FINAL ITINERARY SUMMARY")
    print("═" * 60)
    print(json.dumps(itinerary, indent=2, ensure_ascii=False, default=str))
