from pathlib import Path
from langchain_community.document_loaders import TextLoader

# Find travel.txt in the same folder as this Python script.
file_path = Path(__file__).resolve().parent / "travel.txt"

# Read the file into LangChain documents.
loader = TextLoader(str(file_path), encoding="utf-8")
documents = loader.load()

# Display the result.
print("Number of documents:", len(documents))
print("\nDocument content:")
print(documents[0].page_content)

print("\nMetadata:")
print(documents[0].metadata)