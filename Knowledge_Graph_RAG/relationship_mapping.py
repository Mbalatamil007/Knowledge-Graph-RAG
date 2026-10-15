import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

project_folder = Path(__file__).resolve().parent
load_dotenv(project_folder / ".env")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is missing from .env")

text = (project_folder / "travel.txt").read_text(encoding="utf-8")


# Define one connection between two entities.
class Relationship(BaseModel):
    source: str = Field(description="Source entity name exactly as in the text")
    relation: Literal["CITY_IN", "SERVES", "LOCATED_IN"]
    target: str = Field(description="Target entity name exactly as in the text")


class RelationshipList(BaseModel):
    relationships: list[Relationship] = Field(
        description="All unique relationships explicitly stated in the text"
    )


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

extractor = llm.with_structured_output(
    RelationshipList,
    method="json_schema",
    strict=True,
)

result = extractor.invoke([
    (
        "system",
        "Extract relationships explicitly stated in the document. "
        "Use exact entity names and these directions:\n"
        "CITY_IN: City to Country.\n"
        "SERVES: Airport to City.\n"
        "LOCATED_IN: Attraction to City.\n"
        "Include each relationship only once. "
        "Do not infer additional relationships or use outside knowledge."
    ),
    ("human", text),
])

print(f"\nTotal relationships: {len(result.relationships)}\n")

for relationship in result.relationships:
    print(
        f"{relationship.source} "
        f"--[{relationship.relation}]--> "
        f"{relationship.target}"
    )

# Save the extracted relationships for later steps.
output_path = project_folder / "relationships.json"
output_path.write_text(
    result.model_dump_json(indent=2),
    encoding="utf-8",
)

print(f"\nSaved to: {output_path.name}")