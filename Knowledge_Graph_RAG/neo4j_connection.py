import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load this project's connection settings.
project_folder = Path(__file__).resolve().parent
load_dotenv(project_folder / ".env")

required_variables = [
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD",
]

for variable in required_variables:
    if not os.getenv(variable):
        raise ValueError(f"{variable} is missing from .env")

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]
database = os.getenv("NEO4J_DATABASE", "neo4j")

# Connect and verify that the database is accessible.
with GraphDatabase.driver(
    uri,
    auth=(username, password),
) as driver:
    driver.verify_connectivity()

    with driver.session(database=database) as session:
        result = session.run("RETURN 1 AS connection_test")
        print("Connection test:", result.single()["connection_test"])

    print("Successfully connected to Neo4j AuraDB!")