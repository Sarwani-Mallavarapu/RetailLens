
import os
from typing import TypedDict, Literal

import chromadb
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

# ============================================================
# Configuration
# ============================================================

MOCK_LLM = os.getenv("MOCK_LLM", "1") != "0"

CHROMA_PATH = "support_assistant/chroma_db"
COLLECTION_NAME = "zepto_support_docs"

class FinalAnswer(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

# ============================================================
# State
# ============================================================

class SupportState(TypedDict, total=False):
    query: str
    intent: Literal["policy_question", "general_question"]
    retrieved_chunks: list[str]
    retrieved_ids: list[str]
    answer: dict


# ============================================================
# ChromaDB + Embedding Model
# ============================================================

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(name=COLLECTION_NAME)


# ============================================================
# Node 1: Classify Intent
# ============================================================

def classify_intent(state: SupportState) -> SupportState:
    query = state["query"]
    query_lower = query.lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "cancel",
        "gift card",
        "support hours",
    ]

    # --------------------------------------------------------
    # MOCK_LLM = 1
    # Required graded baseline: keyword heuristic
    # --------------------------------------------------------

    if MOCK_LLM:
        if any(keyword in query_lower for keyword in policy_keywords):
            intent = "policy_question"
        else:
            intent = "general_question"

    # --------------------------------------------------------
    # MOCK_LLM = 0
    # Optional real LLM extension
    # --------------------------------------------------------

    else:
        # Optional LLM implementation can be added here.
        # For now, use the same deterministic classification
        # as a fallback.
        if any(keyword in query_lower for keyword in policy_keywords):
            intent = "policy_question"
        else:
            intent = "general_question"

    return {
        **state,
        "intent": intent,
    }


# ============================================================
# Node 2: Retrieve and Answer
# ============================================================

def retrieve_and_answer(state: SupportState) -> SupportState:
    query = state["query"]

    # --------------------------------------------------------
    # Retrieval always runs
    # --------------------------------------------------------

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
    )

    documents = results.get("documents", [[]])[0]
    ids = results.get("ids", [[]])[0]

    # --------------------------------------------------------
    # No results
    # --------------------------------------------------------

    if not documents:
        response = FinalAnswer(
            answer="No relevant policy information was found.",
            sources=[],
            confidence=0.0,
        )

        return {
            **state,
            "retrieved_chunks": [],
            "retrieved_ids": [],
            "answer": response.model_dump(),
        }

    # --------------------------------------------------------
    # MOCK_LLM = 1
    # Required graded baseline
    # --------------------------------------------------------

    if MOCK_LLM:

        top_chunk_snippet = documents[0][:200]

        response = FinalAnswer(
            answer=f"Based on the retrieved context: {top_chunk_snippet}",
            sources=ids,
            confidence=1.0,
        )

        return {
            **state,
            "retrieved_chunks": documents,
            "retrieved_ids": ids,
            "answer": response.model_dump(),
        }

    # --------------------------------------------------------
    # MOCK_LLM = 0
    # Optional real LLM extension
    # --------------------------------------------------------

    else:

        # Real LLM generation + validation can be implemented here.
        # The raw LLM response must ultimately be validated
        # against FinalAnswer.

        context = "\n\n".join(documents)

        raw_output = {
            "answer": f"LLM answer based on: {context}",
            "sources": ids,
            "confidence": 1.0,
        }

        try:
            response = FinalAnswer.model_validate(raw_output)

            return {
                **state,
                "retrieved_chunks": documents,
                "retrieved_ids": ids,
                "answer": response.model_dump(),
            }

        except Exception:
            error_response = FinalAnswer(
                answer="ERROR: Unable to generate a valid structured response.",
                sources=ids,
                confidence=0.0,
            )

            return {
                **state,
                "retrieved_chunks": documents,
                "retrieved_ids": ids,
                "answer": error_response.model_dump(),
            }


# ============================================================
# Node 3: Direct Answer
# ============================================================

def direct_answer(state: SupportState) -> SupportState:

    # --------------------------------------------------------
    # MOCK_LLM = 1
    # Required graded baseline
    # --------------------------------------------------------

    if MOCK_LLM:

        response = FinalAnswer(
            answer="I can only answer questions about Zepto policies right now.",
            sources=[],
            confidence=1.0,
        )

        return {
            **state,
            "answer": response.model_dump(),
        }

    # --------------------------------------------------------
    # MOCK_LLM = 0
    # Optional real LLM extension
    # --------------------------------------------------------

    else:

        # Real LLM generation will eventually go here.
        raw_output = {
            "answer": "I can only answer questions about Zepto policies right now.",
            "sources": [],
            "confidence": 1.0,
        }

        try:
            response = FinalAnswer.model_validate(raw_output)

            return {
                **state,
                "answer": response.model_dump(),
            }

        except Exception:
            error_response = FinalAnswer(
                answer="ERROR: Unable to generate a valid structured response.",
                sources=[],
                confidence=0.0,
            )

            return {
                **state,
                "answer": error_response.model_dump(),
            }


# ============================================================
# Conditional Routing
# ============================================================

def route_intent(
    state: SupportState,
) -> Literal["retrieve_and_answer", "direct_answer"]:

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


# ============================================================
# Build LangGraph StateGraph
# ============================================================

builder = StateGraph(SupportState)

builder.add_node("classify_intent", classify_intent)
builder.add_node("retrieve_and_answer", retrieve_and_answer)
builder.add_node("direct_answer", direct_answer)

builder.add_edge(START, "classify_intent")

builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer",
    },
)

builder.add_edge("retrieve_and_answer", END)
builder.add_edge("direct_answer", END)

graph = builder.compile()


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":

    queries = [
        "How can I track my delivery?",
        "What is the weather today?",
        "Can I get a refund?",
        "How do I cancel my order?",
    ]

    for query in queries:

        result = graph.invoke({
            "query": query
        })

        print("\n" + "=" * 60)
        print("Query:", query)
        print("Intent:", result["intent"])
        print("Answer:", result["answer"])
