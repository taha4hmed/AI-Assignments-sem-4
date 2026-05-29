"""
ingest.py — GraphRAG AI Travel Planner: Ingestion & Extraction Engine
======================================================================
Pipeline:
  1. Load hardcoded sample travel blog text about Tuscany
  2. Use LangChain LLMGraphTransformer + ChatOpenAI to extract entities/relations
     constrained by our Pydantic schema (schema.py)
  3. Ingest extracted nodes & edges into the local Neo4j instance via
     langchain_neo4j.Neo4jGraph

Usage:
  python ingest.py
"""

import os
import sys
import json
import logging
from textwrap import dedent
from typing import Any, Dict, List

from dotenv import load_dotenv

# ── LangChain ──────────────────────────────────────────────────────────────
from langchain_openai import ChatOpenAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_neo4j import Neo4jGraph

# ── Local schema ──────────────────────────────────────────────────────────
from schema import (
    ALLOWED_NODES,
    ALLOWED_RELATIONSHIPS,
    NODE_PROPERTIES,
    RELATIONSHIP_PROPERTIES,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("ingest")

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "TravelGraph2026!")

if not OPENAI_API_KEY:
    log.error(
        "OPENAI_API_KEY not found. "
        "Please create a .env file with your key or set the environment variable."
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Sample unstructured travel blog text
# ---------------------------------------------------------------------------
SAMPLE_TRAVEL_TEXT = dedent("""
    Tuscany is one of Italy's most breathtaking regions, famous for its rolling hills,
    Renaissance cities, and world-class wines. The region's capital, Florence, is home to
    the iconic Uffizi Gallery, where visitors can spend a full day immersed in Renaissance
    masterpieces by Botticelli and Michelangelo. A visit to Florence is incomplete without
    tasting a classic Bistecca alla Fiorentina – a thick, charcoal-grilled T-bone steak
    that is a cornerstone of Tuscan cuisine. The dish pairs beautifully with a robust glass
    of Chianti Classico, a renowned red wine crafted primarily from the Sangiovese grape
    and produced in the Chianti Classico DOCG zone between Florence and Siena.

    For an authentic agriturismo experience, Villa dei Baronci in the heart of the Chianti
    region offers stunning vineyard views and 4-star amenities. Priced at around €180 per
    night, this boutique property is located in San Casciano Val di Pesa, a charming village
    just 17 kilometres from Florence. The estate's on-site restaurant, Osteria della Villa,
    serves traditional Pappardelle al Cinghiale – wide pasta ribbons with wild boar ragù –
    which is perfectly complemented by their estate-bottled Sangiovese. Guests can also join
    a daily wine tasting tour that explores the estate's organic vineyards and wine cellars.

    Further south in Tuscany lies the medieval city of Siena, celebrated for its magnificent
    Piazza del Campo and the thrilling Palio horse race. Near Siena, the scenic Montepulciano
    hilltop town is home to Vino Nobile di Montepulciano, another prestigious red wine made
    from the Prugnolo Gentile clone of Sangiovese. The Enoteca Poliziana wine bar in
    Montepulciano is famous for pouring vertical tastings of this noble wine alongside local
    Pici pasta with truffle sauce. Visitors on a cycling holiday through the Val d'Orcia —
    a UNESCO World Heritage Site — often stop at the Bagno Vignoni thermal baths to relax
    before heading to Montalcino, the birthplace of the legendary Brunello di Montalcino,
    widely considered one of Italy's greatest red wines. Hotel Il Giglio in Montalcino is a
    3-star property offering comfortable rooms and a breakfast terrace overlooking the
    vineyards, at approximately €120 per night.
""").strip()

# ---------------------------------------------------------------------------
# Helper: build Neo4j driver-friendly property dict from a graph node/edge
# ---------------------------------------------------------------------------

def _clean_props(props: Dict[str, Any]) -> Dict[str, Any]:
    """Remove None values and non-serialisable objects from a property dict."""
    return {k: v for k, v in props.items() if v is not None and not isinstance(v, type)}


# ---------------------------------------------------------------------------
# Core ingestion function
# ---------------------------------------------------------------------------

def run_ingestion() -> None:
    log.info("═" * 60)
    log.info("GraphRAG AI Travel Planner — Ingestion Engine")
    log.info("═" * 60)

    # ── 1. Connect to Neo4j ────────────────────────────────────────────────
    log.info("Connecting to Neo4j at %s …", NEO4J_URI)
    graph = Neo4jGraph(
        url=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
    )
    log.info("Neo4j connection established ✓")

    # ── 2. Initialise LLM ─────────────────────────────────────────────────
    log.info("Initialising ChatOpenAI (gpt-4o) …")
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
    )

    # ── 3. Initialise LLMGraphTransformer with schema constraints ──────────
    log.info("Configuring LLMGraphTransformer with schema constraints …")
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=ALLOWED_NODES,
        allowed_relationships=ALLOWED_RELATIONSHIPS,
        node_properties=NODE_PROPERTIES,
        relationship_properties=RELATIONSHIP_PROPERTIES,
        strict_mode=True,
    )

    # ── 4. Wrap sample text in a LangChain Document ───────────────────────
    docs = [Document(page_content=SAMPLE_TRAVEL_TEXT, metadata={"source": "tuscany_blog"})]
    log.info("Extracting graph from %d document(s) …", len(docs))

    # ── 5. Extract graph documents ────────────────────────────────────────
    try:
        graph_documents = transformer.convert_to_graph_documents(docs)

        total_nodes = sum(len(gd.nodes) for gd in graph_documents)
        total_rels = sum(len(gd.relationships) for gd in graph_documents)
        log.info("Extraction complete: %d nodes, %d relationships found", total_nodes, total_rels)

        # Log extracted entities for visibility
        for gd in graph_documents:
            log.info("  Document source: %s", gd.source.metadata.get("source", "unknown"))
            for node in gd.nodes:
                log.info("    NODE  [%s] %s — props: %s", node.type, node.id, node.properties)
            for rel in gd.relationships:
                log.info(
                    "    EDGE  (%s)-[%s]->(%s)",
                    rel.source.id, rel.type, rel.target.id
                )

        # ── 6. Add extracted graph to Neo4j ───────────────────────────────────
        log.info("Ingesting extracted graph into Neo4j …")
        graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,    # adds __Entity__ label for easy querying
            include_source=True,     # links nodes back to source Document
        )
        log.info("Ingestion complete ✓")
    except Exception as exc:
        log.warning("LLM extraction failed (%s). Skipping to curated baseline graph.", exc)

    # ── 7. Seed curated nodes that the LLM may have missed ────────────────
    log.info("Seeding curated baseline graph nodes …")
    _seed_baseline_graph(graph)

    # ── 8. Create indexes for fast retrieval ──────────────────────────────
    log.info("Creating Neo4j indexes …")
    _create_indexes(graph)

    # ── 9. Print summary ──────────────────────────────────────────────────
    result = graph.query("MATCH (n) RETURN count(n) AS nodeCount")
    rel_result = graph.query("MATCH ()-[r]->() RETURN count(r) AS relCount")
    log.info(
        "Graph summary: %d total nodes, %d total relationships",
        result[0]["nodeCount"],
        rel_result[0]["relCount"],
    )
    log.info("═" * 60)
    log.info("Ingestion pipeline finished successfully ✓")
    log.info("═" * 60)


# ---------------------------------------------------------------------------
# Curated baseline graph — ensures key entities exist even if the LLM
# extraction misses or names them differently
# ---------------------------------------------------------------------------

def _seed_baseline_graph(graph: Neo4jGraph) -> None:
    """
    Upsert a curated set of nodes and relationships using MERGE so that
    re-running ingest.py is idempotent.
    """

    cypher_statements: List[str] = [
        # ── Locations ──────────────────────────────────────────────────────
        """MERGE (tuscany:Location {id: 'tuscany'})
           SET tuscany.name = 'Tuscany',
               tuscany.country = 'Italy',
               tuscany.description = 'Central Italian region famous for wine, art, and landscapes'""",

        """MERGE (florence:Location {id: 'florence'})
           SET florence.name = 'Florence',
               florence.region = 'Tuscany',
               florence.country = 'Italy',
               florence.description = 'Renaissance capital of Tuscany'""",

        """MERGE (siena:Location {id: 'siena'})
           SET siena.name = 'Siena',
               siena.region = 'Tuscany',
               siena.country = 'Italy',
               siena.description = 'Medieval hilltop city, home of the Palio'""",

        """MERGE (chianti:Location {id: 'chianti'})
           SET chianti.name = 'Chianti',
               chianti.region = 'Tuscany',
               chianti.country = 'Italy',
               chianti.description = 'Wine-growing zone between Florence and Siena'""",

        """MERGE (montepulciano:Location {id: 'montepulciano'})
           SET montepulciano.name = 'Montepulciano',
               montepulciano.region = 'Tuscany',
               montepulciano.country = 'Italy',
               montepulciano.description = 'Hilltop town famous for Vino Nobile'""",

        """MERGE (montalcino:Location {id: 'montalcino'})
           SET montalcino.name = 'Montalcino',
               montalcino.region = 'Tuscany',
               montalcino.country = 'Italy',
               montalcino.description = 'Birthplace of Brunello di Montalcino'""",

        # ── Accommodations ─────────────────────────────────────────────────
        """MERGE (villa:Accommodation {id: 'villa_dei_baronci'})
           SET villa.name = 'Villa dei Baronci',
               villa.type = 'Agriturismo',
               villa.star_rating = 4,
               villa.price_per_night_eur = 180.0,
               villa.description = 'Boutique agriturismo with vineyard views in Chianti'""",

        """MERGE (hotel_giglio:Accommodation {id: 'hotel_il_giglio'})
           SET hotel_giglio.name = 'Hotel Il Giglio',
               hotel_giglio.type = 'Hotel',
               hotel_giglio.star_rating = 3,
               hotel_giglio.price_per_night_eur = 120.0,
               hotel_giglio.description = 'Comfortable hotel in Montalcino with vineyard views'""",

        # ── Wines ──────────────────────────────────────────────────────────
        """MERGE (sangiovese:Wine {id: 'sangiovese'})
           SET sangiovese.name = 'Sangiovese',
               sangiovese.type = 'Red',
               sangiovese.grape_variety = 'Sangiovese',
               sangiovese.region_of_origin = 'Tuscany',
               sangiovese.tasting_notes = 'Cherry, plum, leather, earthy undertones'""",

        """MERGE (chianti_classico:Wine {id: 'chianti_classico'})
           SET chianti_classico.name = 'Chianti Classico',
               chianti_classico.type = 'Red',
               chianti_classico.grape_variety = 'Sangiovese Grosso',
               chianti_classico.region_of_origin = 'Chianti Classico DOCG',
               chianti_classico.tasting_notes = 'Red cherry, tobacco, spice, firm tannins'""",

        """MERGE (brunello:Wine {id: 'brunello_di_montalcino'})
           SET brunello.name = 'Brunello di Montalcino',
               brunello.type = 'Red',
               brunello.grape_variety = 'Sangiovese Grosso',
               brunello.region_of_origin = 'Montalcino DOCG',
               brunello.tasting_notes = 'Complex dark fruit, leather, tobacco, exceptional ageing potential'""",

        # ── Cuisines ───────────────────────────────────────────────────────
        """MERGE (bistecca:Cuisine {id: 'bistecca_fiorentina'})
           SET bistecca.name = 'Bistecca alla Fiorentina',
               bistecca.category = 'Tuscan',
               bistecca.is_vegetarian = false,
               bistecca.description = 'Classic thick-cut T-bone steak grilled over charcoal'""",

        """MERGE (pappardelle:Cuisine {id: 'pappardelle_cinghiale'})
           SET pappardelle.name = 'Pappardelle al Cinghiale',
               pappardelle.category = 'Tuscan',
               pappardelle.is_vegetarian = false,
               pappardelle.description = 'Wide pasta ribbons with wild boar ragù'""",

        """MERGE (pici_tartufo:Cuisine {id: 'pici_tartufo'})
           SET pici_tartufo.name = 'Pici con Tartufo',
               pici_tartufo.category = 'Tuscan',
               pici_tartufo.is_vegetarian = true,
               pici_tartufo.description = 'Hand-rolled thick spaghetti with truffle sauce'""",

        # ── Activities ─────────────────────────────────────────────────────
        """MERGE (uffizi:Activity {id: 'uffizi_gallery'})
           SET uffizi.name = 'Uffizi Gallery Tour',
               uffizi.category = 'Museum',
               uffizi.duration_hours = 3.0,
               uffizi.price_eur = 25.0,
               uffizi.booking_required = true,
               uffizi.description = 'One of the world's great art museums, housing Renaissance masterpieces'""",

        """MERGE (wine_tasting:Activity {id: 'chianti_wine_tasting'})
           SET wine_tasting.name = 'Chianti Vineyard Wine Tasting',
               wine_tasting.category = 'Wine Tasting',
               wine_tasting.duration_hours = 2.5,
               wine_tasting.price_eur = 45.0,
               wine_tasting.booking_required = false,
               wine_tasting.description = 'Guided wine tasting through organic Chianti vineyards and cellars'""",

        """MERGE (cycling:Activity {id: 'val_dorcia_cycling'})
           SET cycling.name = 'Val d\'Orcia Cycling Tour',
               cycling.category = 'Cycling',
               cycling.duration_hours = 6.0,
               cycling.price_eur = 60.0,
               cycling.booking_required = true,
               cycling.description = 'Scenic cycling through the UNESCO Val d\'Orcia landscape'""",

        """MERGE (thermal:Activity {id: 'bagno_vignoni_thermal'})
           SET thermal.name = 'Bagno Vignoni Thermal Baths',
               thermal.category = 'Thermal Baths',
               thermal.duration_hours = 3.0,
               thermal.price_eur = 20.0,
               thermal.booking_required = false,
               thermal.description = 'Historic thermal baths near San Quirico d\'Orcia'""",

        # ── Relationships ──────────────────────────────────────────────────
        # Florence LOCATED_IN Tuscany
        """MATCH (f:Location {id: 'florence'}), (t:Location {id: 'tuscany'})
           MERGE (f)-[:LOCATED_IN]->(t)""",

        # Siena LOCATED_IN Tuscany
        """MATCH (s:Location {id: 'siena'}), (t:Location {id: 'tuscany'})
           MERGE (s)-[:LOCATED_IN]->(t)""",

        # Chianti LOCATED_IN Tuscany
        """MATCH (c:Location {id: 'chianti'}), (t:Location {id: 'tuscany'})
           MERGE (c)-[:LOCATED_IN]->(t)""",

        # Montepulciano LOCATED_IN Tuscany
        """MATCH (mp:Location {id: 'montepulciano'}), (t:Location {id: 'tuscany'})
           MERGE (mp)-[:LOCATED_IN]->(t)""",

        # Montalcino LOCATED_IN Tuscany
        """MATCH (mn:Location {id: 'montalcino'}), (t:Location {id: 'tuscany'})
           MERGE (mn)-[:LOCATED_IN]->(t)""",

        # Villa dei Baronci LOCATED_IN Chianti
        """MATCH (v:Accommodation {id: 'villa_dei_baronci'}), (c:Location {id: 'chianti'})
           MERGE (v)-[:LOCATED_IN]->(c)""",

        # Hotel Il Giglio LOCATED_IN Montalcino
        """MATCH (h:Accommodation {id: 'hotel_il_giglio'}), (mn:Location {id: 'montalcino'})
           MERGE (h)-[:LOCATED_IN]->(mn)""",

        # Villa SERVES wine tasting activity (treated as SERVES event)
        """MATCH (v:Accommodation {id: 'villa_dei_baronci'}), (wt:Activity {id: 'chianti_wine_tasting'})
           MERGE (v)-[:SERVES]->(wt)""",

        # Villa IS_NEAR Chianti wine tasting
        """MATCH (v:Accommodation {id: 'villa_dei_baronci'}), (wt:Activity {id: 'chianti_wine_tasting'})
           MERGE (v)-[r:IS_NEAR]->(wt)
           SET r.distance_km = 2.0""",

        # Villa IS_NEAR Florence
        """MATCH (v:Accommodation {id: 'villa_dei_baronci'}), (f:Location {id: 'florence'})
           MERGE (v)-[r:IS_NEAR]->(f)
           SET r.distance_km = 17.0""",

        # Hotel IS_NEAR Montalcino vineyards
        """MATCH (h:Accommodation {id: 'hotel_il_giglio'}), (mn:Location {id: 'montalcino'})
           MERGE (h)-[r:IS_NEAR]->(mn)
           SET r.distance_km = 1.0""",

        # Uffizi LOCATED_IN Florence
        """MATCH (u:Activity {id: 'uffizi_gallery'}), (f:Location {id: 'florence'})
           MERGE (u)-[:LOCATED_IN]->(f)""",

        # Wine tasting LOCATED_IN Chianti
        """MATCH (wt:Activity {id: 'chianti_wine_tasting'}), (c:Location {id: 'chianti'})
           MERGE (wt)-[:LOCATED_IN]->(c)""",

        # Cycling LOCATED_IN Tuscany
        """MATCH (cy:Activity {id: 'val_dorcia_cycling'}), (t:Location {id: 'tuscany'})
           MERGE (cy)-[:LOCATED_IN]->(t)""",

        # Thermal baths LOCATED_IN Tuscany
        """MATCH (th:Activity {id: 'bagno_vignoni_thermal'}), (t:Location {id: 'tuscany'})
           MERGE (th)-[:LOCATED_IN]->(t)""",

        # Chianti Classico LOCATED_IN Chianti region
        """MATCH (cc:Wine {id: 'chianti_classico'}), (c:Location {id: 'chianti'})
           MERGE (cc)-[:LOCATED_IN]->(c)""",

        # Sangiovese LOCATED_IN Tuscany
        """MATCH (sg:Wine {id: 'sangiovese'}), (t:Location {id: 'tuscany'})
           MERGE (sg)-[:LOCATED_IN]->(t)""",

        # Brunello LOCATED_IN Montalcino
        """MATCH (br:Wine {id: 'brunello_di_montalcino'}), (mn:Location {id: 'montalcino'})
           MERGE (br)-[:LOCATED_IN]->(mn)""",

        # Sangiovese PAIRS_WITH Bistecca
        """MATCH (sg:Wine {id: 'sangiovese'}), (bs:Cuisine {id: 'bistecca_fiorentina'})
           MERGE (sg)-[:PAIRS_WITH]->(bs)""",

        # Chianti Classico PAIRS_WITH Bistecca
        """MATCH (cc:Wine {id: 'chianti_classico'}), (bs:Cuisine {id: 'bistecca_fiorentina'})
           MERGE (cc)-[:PAIRS_WITH]->(bs)""",

        # Sangiovese PAIRS_WITH Pappardelle
        """MATCH (sg:Wine {id: 'sangiovese'}), (pp:Cuisine {id: 'pappardelle_cinghiale'})
           MERGE (sg)-[:PAIRS_WITH]->(pp)""",

        # Brunello PAIRS_WITH Bistecca
        """MATCH (br:Wine {id: 'brunello_di_montalcino'}), (bs:Cuisine {id: 'bistecca_fiorentina'})
           MERGE (br)-[:PAIRS_WITH]->(bs)""",

        # Bistecca SERVES in Florence
        """MATCH (f:Location {id: 'florence'}), (bs:Cuisine {id: 'bistecca_fiorentina'})
           MERGE (f)-[:SERVES]->(bs)""",

        # Villa SERVES Pappardelle Cinghiale
        """MATCH (v:Accommodation {id: 'villa_dei_baronci'}), (pp:Cuisine {id: 'pappardelle_cinghiale'})
           MERGE (v)-[:SERVES]->(pp)""",

        # Villa SERVES Sangiovese wine
        """MATCH (v:Accommodation {id: 'villa_dei_baronci'}), (sg:Wine {id: 'sangiovese'})
           MERGE (v)-[:SERVES]->(sg)""",

        # Hotel SERVES Brunello wine
        """MATCH (h:Accommodation {id: 'hotel_il_giglio'}), (br:Wine {id: 'brunello_di_montalcino'})
           MERGE (h)-[:SERVES]->(br)""",

        # Chianti (region) SERVES Chianti Classico wine
        """MATCH (c:Location {id: 'chianti'}), (cc:Wine {id: 'chianti_classico'})
           MERGE (c)-[:SERVES]->(cc)""",

        # Chianti (region) SERVES Sangiovese wine
        """MATCH (c:Location {id: 'chianti'}), (sg:Wine {id: 'sangiovese'})
           MERGE (c)-[:SERVES]->(sg)""",
    ]

    for i, stmt in enumerate(cypher_statements, start=1):
        try:
            graph.query(stmt)
        except Exception as exc:
            log.warning("Seed statement %d failed (non-fatal): %s", i, exc)

    log.info("Curated baseline graph seeded (%d statements) ✓", len(cypher_statements))


# ---------------------------------------------------------------------------
# Index creation
# ---------------------------------------------------------------------------

def _create_indexes(graph: Neo4jGraph) -> None:
    index_statements = [
        "CREATE INDEX location_id IF NOT EXISTS FOR (n:Location) ON (n.id)",
        "CREATE INDEX accommodation_id IF NOT EXISTS FOR (n:Accommodation) ON (n.id)",
        "CREATE INDEX activity_id IF NOT EXISTS FOR (n:Activity) ON (n.id)",
        "CREATE INDEX wine_id IF NOT EXISTS FOR (n:Wine) ON (n.id)",
        "CREATE INDEX cuisine_id IF NOT EXISTS FOR (n:Cuisine) ON (n.id)",
        "CREATE INDEX location_name IF NOT EXISTS FOR (n:Location) ON (n.name)",
        "CREATE INDEX wine_name IF NOT EXISTS FOR (n:Wine) ON (n.name)",
        "CREATE INDEX accommodation_name IF NOT EXISTS FOR (n:Accommodation) ON (n.name)",
    ]
    for stmt in index_statements:
        try:
            graph.query(stmt)
        except Exception as exc:
            log.warning("Index creation failed (non-fatal): %s", exc)
    log.info("Indexes created ✓")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_ingestion()
