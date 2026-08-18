"""
Step 3 - Answer a chat question using the RAG index, via a local Ollama model,
orchestrated through CrewAI.

Defines one CrewAI Agent with a custom tool that embeds the query and
searches the Qdrant collection built by 01_build_rag.py. The agent's LLM is
a local Ollama chat model (README.md: "using my ollama") - no external API
key involved.

Usage:
    python scripts/03_chat_with_rag.py --question "What laptops do you have in stock?"
"""

import argparse
import sys
from pathlib import Path

# CrewAI's console logging writes emoji; Windows' default console codepage
# can't encode them, which otherwise spams "charmap codec" errors.
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from common import config, ollama_client  # noqa: E402  (must run before crewai import - sets telemetry env vars)

from crewai import LLM, Agent, Crew, Process, Task  # noqa: E402
from crewai.tools import BaseTool  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402
from qdrant_client import QdrantClient  # noqa: E402

TOP_K = 5


class ProductSearchInput(BaseModel):
    query: str = Field(..., description="Natural-language question about the product catalog.")


class ProductCatalogSearchTool(BaseTool):
    name: str = "product_catalog_search"
    description: str = (
        "Searches the product catalog RAG index (Qdrant) for products relevant to a "
        "natural-language question. Returns the matching product descriptions with "
        "price and stock status. Always use this before answering a catalog question."
    )
    args_schema: type[BaseModel] = ProductSearchInput

    def _run(self, query: str) -> str:
        client = QdrantClient(url=config.QDRANT_URL)
        query_vector = ollama_client.embed(query)
        hits = client.query_points(
            collection_name=config.COLLECTION_NAME,
            query=query_vector,
            limit=TOP_K,
        ).points
        if not hits:
            return "No matching products found in the catalog."
        return "\n".join(f"- {hit.payload['text']}" for hit in hits)


def build_crew(question: str) -> Crew:
    llm = LLM(model=f"ollama/{config.OLLAMA_CHAT_MODEL}", base_url=config.OLLAMA_BASE_URL)

    agent = Agent(
        role="Product Catalog Assistant",
        goal="Answer customer questions about the product catalog accurately, using only retrieved context.",
        backstory=(
            "You work the storefront help desk. You never guess at prices, stock, or "
            "product names - you always look them up first."
        ),
        llm=llm,
        tools=[ProductCatalogSearchTool()],
        verbose=True,
    )

    task = Task(
        description=(
            f"Answer this customer question: {question}\n\n"
            "Use the product_catalog_search tool at least once before answering. "
            "Base your answer only on what the tool returns - if it doesn't cover "
            "the question, say so instead of guessing."
        ),
        expected_output="A concise, accurate answer grounded in the retrieved product data.",
        agent=agent,
    )

    return Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)


def main():
    parser = argparse.ArgumentParser(description="Chat with the product catalog RAG index via local Ollama + CrewAI.")
    parser.add_argument("--question", required=True, help="Question to ask the assistant.")
    args = parser.parse_args()

    crew = build_crew(args.question)
    result = crew.kickoff()

    print("\n" + "=" * 60)
    print("ANSWER")
    print("=" * 60)
    print(result.raw)

    usage = crew.usage_metrics
    if usage:
        print("\n" + "=" * 60)
        print("TOKEN USAGE (from CrewAI/Ollama)")
        print("=" * 60)
        print(usage)


if __name__ == "__main__":
    main()
