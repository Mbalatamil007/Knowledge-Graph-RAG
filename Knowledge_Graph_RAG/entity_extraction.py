import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Load the API key from this project's .env file.
project_folder = Path(__file__).resolve().parent
load_dotenv(project_folder / ".env")

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is missing from .env")

# Read the travel document.
text = (project_folder / "travel.txt").read_text(encoding="utf-8")


# Define the structure of one entity.
class Entity(BaseModel):
    name: str = Field(description="The entity's name exactly as in the text")
    type: Literal["City", "Country", "Airport", "Attraction"]


# Define the structure of the complete response.
class EntityList(BaseModel):
    entities: list[Entity] = Field(
        description="All unique entities mentioned in the document"
    )


# Connect to the OpenAI model through LangChain.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

extractor = llm.with_structured_output(
    EntityList,
    method="json_schema",
    strict=True,
)

# Ask the model to identify entities.
result = extractor.invoke([
    (
        "system",
        "Extract all cities, countries, airports, and attractions "
        "explicitly mentioned in the supplied document. "
        "Use their exact names. Include each entity only once. "
        "Do not add facts or entities from outside the document."
    ),
    ("human", text),
])

# Display the extracted entities.
print(f"\nTotal entities: {len(result.entities)}\n")

for entity in result.entities:
    print(f"{entity.name} -> {entity.type}")