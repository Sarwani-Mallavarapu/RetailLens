from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# Paths
BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"


# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# Create persistent ChromaDB client
client = chromadb.PersistentClient(path=str(CHROMA_DIR))


# Create/get collection
collection = client.get_or_create_collection(
    name="zepto_support_docs",
    metadata={"hnsw:space": "cosine"}
)


def load_documents():
    documents = []
    ids = []
    metadatas = []

    for file_path in sorted(DOCS_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        documents.append(text)
        ids.append(file_path.stem)
        metadatas.append({
            "document_id": file_path.stem,
            "source": file_path.name
        })

    return documents, ids, metadatas


def main():
    documents, ids, metadatas = load_documents()

    if len(documents) != 8:
        raise ValueError(
            f"Expected 8 documents, but found {len(documents)}."
        )

    # One chunk per document.
    # The corpus documents are short enough for this approach.
    chunks = documents
    chunk_ids = ids
    chunk_metadatas = metadatas

    # Generate embeddings
    embeddings = embedding_model.encode(
        chunks,
        normalize_embeddings=True
    ).tolist()

    # Store in ChromaDB
    collection.upsert(
        ids=chunk_ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=chunk_metadatas
    )

    print(f"Loaded documents : {len(documents)}")
    print(f"Stored chunks     : {len(chunks)}")
    print(f"Collection        : {collection.name}")
    print(f"ChromaDB path     : {CHROMA_DIR}")

    # Verify storage
    result = collection.get(
        include=["documents", "metadatas"]
    )

    print(f"Verified chunks   : {len(result['ids'])}")


if __name__ == "__main__":
    main()