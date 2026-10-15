import os
from pathlib import Path
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load your existing connection settings.
load_dotenv(Path(__file__).resolve().parent / ".env")

city_name = "Chennai"

# $city_name is a parameter whose value we supply below.
query = """
MATCH (attraction:Attraction)-[:LOCATED_IN]->(city:City {name: $city_name})
RETURN attraction.name AS attraction
ORDER BY attraction
"""

with GraphDatabase.driver(
    os.environ["NEO4J_URI"],
    auth=(
        os.environ["NEO4J_USERNAME"],
        os.environ["NEO4J_PASSWORD"],
    ),
) as driver:
    with driver.session(
        database=os.getenv("NEO4J_DATABASE", "neo4j")
    ) as session:
        results = session.run(query, city_name=city_name)
        attractions = [record["attraction"] for record in results]

print(f"\nAttractions in {city_name}:")

if attractions:
    for attraction in attractions:
        print(f"- {attraction}")
else:
    print("No attractions found in the graph.")


question = f"Which attractions are in {city_name}?"

if attractions:
    context = "\n".join(
        f"{attraction} is located in {city_name}."
        for attraction in attractions
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    response = llm.invoke([
        (
            "system",
            "Answer the question using only the supplied graph facts. "
            "Do not add outside information. "
            "If the facts do not answer the question, say you don't know. "
            "Keep the answer short."
        ),
        (
            "human",
            f"Graph facts:\n{context}\n\nQuestion: {question}"
        ),
    ])

    print("\nQuestion:", question)
    print("Answer:", response.content)
else:
    print("\nNo graph facts found, so answer generation was skipped.")

city_name = input(
    "Enter a city (Chennai, New Delhi, Paris, London): "
).strip()