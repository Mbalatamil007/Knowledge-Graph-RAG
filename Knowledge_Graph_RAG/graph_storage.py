import json
import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

project_folder = Path(__file__).resolve().parent
load_dotenv(project_folder / ".env")

# Read the relationships we already extracted.
data = json.loads(
    (project_folder / "relationships.json").read_text(encoding="utf-8")
)

# Define the source and target types for each relationship.
relationship_types = {
    "CITY_IN": ("City", "Country"),
    "SERVES": ("Airport", "City"),
    "LOCATED_IN": ("Attraction", "City"),
}


def store_relationships(tx):
    for item in data["relationships"]:
        relation = item["relation"]

        if relation not in relationship_types:
            raise ValueError(f"Unsupported relationship: {relation}")

        source_type, target_type = relationship_types[relation]

        # Normalize the naming difference found earlier.
        source = item["source"].strip()
        target = item["target"].strip()

        if target_type == "Country" and target == "the United Kingdom":
            target = "United Kingdom"

        # Labels and relationship types come from our allowed mapping.
        # Entity names are passed separately as query parameters.
        query = f"""
        MERGE (source:TravelEntity:{source_type} {{name: $source}})
        MERGE (target:TravelEntity:{target_type} {{name: $target}})
        MERGE (source)-[:{relation}]->(target)
        """

        tx.run(query, source=source, target=target).consume()


with GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(
        os.environ["NEO4J_USERNAME"],
        os.environ["NEO4J_PASSWORD"],
    ),
) as driver:
    driver.verify_connectivity()

    with driver.session(
        database=os.getenv("NEO4J_DATABASE", "neo4j")
    ) as session:
        session.execute_write(store_relationships)

        node_count = session.run(
            "MATCH (n:TravelEntity) RETURN count(n) AS total"
        ).single()["total"]

        relationship_count = session.run(
            """
            MATCH (:TravelEntity)-[r]->(:TravelEntity)
            RETURN count(r) AS total
            """
        ).single()["total"]

        print("Travel graph stored successfully!")
        print("Total nodes:", node_count)
        print("Total relationships:", relationship_count)