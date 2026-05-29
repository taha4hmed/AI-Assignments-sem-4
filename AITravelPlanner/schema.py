"""
schema.py — GraphRAG AI Travel Planner Ontology
================================================
This module defines the full Pydantic v2 schema for the travel knowledge graph.
It acts as our operational ontology, replacing a manual Protégé export, and is
consumed by both the ingestion engine (ingest.py) and the GraphRAG agent (agent.py).

Node hierarchy:
    Entity
    ├── Location
    ├── Accommodation
    ├── Activity
    ├── Wine
    └── Cuisine

Relationship types (Edges):
    LOCATED_IN   – Accommodation / Activity is located inside a Location
    SERVES       – Location / Accommodation serves a Cuisine or Wine
    PAIRS_WITH   – Wine pairs with a Cuisine (bidirectional by convention)
    IS_NEAR      – Accommodation is near an Activity or Location
"""

from __future__ import annotations

from enum import Enum
from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class WineType(str, Enum):
    RED = "Red"
    WHITE = "White"
    ROSÉ = "Rosé"
    SPARKLING = "Sparkling"
    DESSERT = "Dessert"


class CuisineCategory(str, Enum):
    ITALIAN = "Italian"
    MEDITERRANEAN = "Mediterranean"
    TUSCAN = "Tuscan"
    VEGETARIAN = "Vegetarian"
    SEAFOOD = "Seafood"
    STREET_FOOD = "Street Food"
    FINE_DINING = "Fine Dining"


class AccommodationType(str, Enum):
    HOTEL = "Hotel"
    AGRITURISMO = "Agriturismo"
    VILLA = "Villa"
    HOSTEL = "Hostel"
    BED_AND_BREAKFAST = "Bed & Breakfast"
    BOUTIQUE = "Boutique Hotel"


class ActivityCategory(str, Enum):
    WINE_TASTING = "Wine Tasting"
    MUSEUM = "Museum"
    HIKING = "Hiking"
    CYCLING = "Cycling"
    COOKING_CLASS = "Cooking Class"
    SIGHTSEEING = "Sightseeing"
    BEACH = "Beach"
    THERMAL_BATHS = "Thermal Baths"


# ---------------------------------------------------------------------------
# Node Models
# ---------------------------------------------------------------------------

class Location(BaseModel):
    """A geographical location: city, town, region, or landmark."""

    id: str = Field(..., description="Unique identifier, e.g. 'tuscany' or 'florence'")
    name: str = Field(..., description="Human-readable name, e.g. 'Florence'")
    region: Optional[str] = Field(None, description="Parent region, e.g. 'Tuscany'")
    country: str = Field(default="Italy", description="Country")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    description: Optional[str] = Field(None, max_length=1000)
    label: Literal["Location"] = "Location"

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Location name must not be empty")
        return v.strip().title()


class Accommodation(BaseModel):
    """A place to stay: hotel, villa, agriturismo, etc."""

    id: str = Field(..., description="Unique identifier, e.g. 'villa_dei_baronci'")
    name: str = Field(..., description="Property name, e.g. 'Villa dei Baronci'")
    type: AccommodationType = Field(..., description="Category of accommodation")
    star_rating: Optional[int] = Field(None, ge=1, le=5)
    price_per_night_eur: Optional[float] = Field(None, ge=0)
    amenities: List[str] = Field(default_factory=list)
    description: Optional[str] = Field(None, max_length=1000)
    label: Literal["Accommodation"] = "Accommodation"

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Accommodation name must not be empty")
        return v.strip()


class Activity(BaseModel):
    """A tourist activity or point of interest."""

    id: str = Field(..., description="Unique identifier, e.g. 'uffizi_gallery'")
    name: str = Field(..., description="Activity name, e.g. 'Uffizi Gallery Tour'")
    category: ActivityCategory = Field(..., description="Type of activity")
    duration_hours: Optional[float] = Field(None, ge=0.5, le=24)
    price_eur: Optional[float] = Field(None, ge=0)
    booking_required: bool = Field(default=False)
    description: Optional[str] = Field(None, max_length=1000)
    label: Literal["Activity"] = "Activity"


class Wine(BaseModel):
    """A wine variety or specific label."""

    id: str = Field(..., description="Unique identifier, e.g. 'sangiovese'")
    name: str = Field(..., description="Wine name, e.g. 'Sangiovese'")
    type: WineType = Field(..., description="Red, White, Rosé, etc.")
    grape_variety: Optional[str] = Field(None, description="Primary grape, e.g. 'Sangiovese Grosso'")
    region_of_origin: Optional[str] = Field(None, description="DOC/DOCG region")
    vintage_year: Optional[int] = Field(None, ge=1900, le=2030)
    tasting_notes: Optional[str] = Field(None, max_length=500)
    food_pairing_suggestions: List[str] = Field(default_factory=list)
    label: Literal["Wine"] = "Wine"


class Cuisine(BaseModel):
    """A dish, meal type, or culinary tradition."""

    id: str = Field(..., description="Unique identifier, e.g. 'bistecca_fiorentina'")
    name: str = Field(..., description="Dish or cuisine name, e.g. 'Bistecca alla Fiorentina'")
    category: CuisineCategory = Field(..., description="Cuisine category")
    ingredients: List[str] = Field(default_factory=list)
    allergens: List[str] = Field(default_factory=list)
    is_vegetarian: bool = Field(default=False)
    is_vegan: bool = Field(default=False)
    description: Optional[str] = Field(None, max_length=1000)
    label: Literal["Cuisine"] = "Cuisine"


# Union type for any graph node
GraphNode = Union[Location, Accommodation, Activity, Wine, Cuisine]


# ---------------------------------------------------------------------------
# Relationship / Edge Models
# ---------------------------------------------------------------------------

class RelationshipBase(BaseModel):
    """Abstract base for all directed graph relationships."""

    source_id: str = Field(..., description="ID of the source node")
    target_id: str = Field(..., description="ID of the target node")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0,
                              description="Extraction confidence score [0, 1]")
    source_text_excerpt: Optional[str] = Field(
        None, max_length=300,
        description="Snippet from the source document that supports this relationship"
    )


class LocatedIn(RelationshipBase):
    """
    LOCATED_IN — An Accommodation or Activity is physically located in a Location.

    Example: Villa dei Baronci  --[LOCATED_IN]--> Chianti
    """
    type: Literal["LOCATED_IN"] = "LOCATED_IN"


class Serves(RelationshipBase):
    """
    SERVES — A Location or Accommodation serves a particular Cuisine or Wine.

    Example: Osteria di Passignano --[SERVES]--> Bistecca alla Fiorentina
    """
    type: Literal["SERVES"] = "SERVES"


class PairsWith(RelationshipBase):
    """
    PAIRS_WITH — A Wine pairs well with a Cuisine (gastronomic affinity).

    Example: Sangiovese --[PAIRS_WITH]--> Bistecca alla Fiorentina
    """
    type: Literal["PAIRS_WITH"] = "PAIRS_WITH"


class IsNear(RelationshipBase):
    """
    IS_NEAR — An Accommodation is in close proximity to a Location or Activity.

    Example: Villa dei Baronci --[IS_NEAR]--> Greve in Chianti Wine Tasting
    """
    type: Literal["IS_NEAR"] = "IS_NEAR"
    distance_km: Optional[float] = Field(None, ge=0,
                                          description="Approximate distance in kilometres")


# Union type for any graph edge
GraphEdge = Union[LocatedIn, Serves, PairsWith, IsNear]


# ---------------------------------------------------------------------------
# Top-level Knowledge Graph Container
# ---------------------------------------------------------------------------

class TravelKnowledgeGraph(BaseModel):
    """
    Root container representing the full extracted knowledge graph.

    This is the output type returned by the ingestion engine after LLM extraction.
    """

    nodes: List[GraphNode] = Field(default_factory=list,
                                   description="All extracted graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list,
                                   description="All extracted graph relationships")

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def summary(self) -> str:
        type_counts: dict[str, int] = {}
        for node in self.nodes:
            label = node.label  # type: ignore[union-attr]
            type_counts[label] = type_counts.get(label, 0) + 1
        edge_type_counts: dict[str, int] = {}
        for edge in self.edges:
            t = edge.type  # type: ignore[union-attr]
            edge_type_counts[t] = edge_type_counts.get(t, 0) + 1
        return (
            f"TravelKnowledgeGraph — {self.node_count()} nodes, {self.edge_count()} edges\n"
            f"  Nodes:  {type_counts}\n"
            f"  Edges:  {edge_type_counts}"
        )


# ---------------------------------------------------------------------------
# LangChain-compatible schema descriptor (used by LLMGraphTransformer)
# ---------------------------------------------------------------------------

# Allowed node labels for LLMGraphTransformer constraint
ALLOWED_NODES = ["Location", "Accommodation", "Activity", "Wine", "Cuisine"]

# Allowed relationship types for LLMGraphTransformer constraint
ALLOWED_RELATIONSHIPS = ["LOCATED_IN", "SERVES", "PAIRS_WITH", "IS_NEAR"]

# Relationship property schema for graph transformer hints
NODE_PROPERTIES = ["name", "description", "type", "region", "country",
                   "star_rating", "price_per_night_eur", "grape_variety",
                   "region_of_origin", "tasting_notes", "category",
                   "duration_hours", "booking_required"]

RELATIONSHIP_PROPERTIES = ["confidence", "distance_km"]
