import json
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# === File paths ===
qa_index_path = "/root/MyPersonalServerLite/serverlite/stevenai/models/qa_index.faiss"
qa_meta_path = "/root/MyPersonalServerLite/serverlite/stevenai/models/qa_metadata.pkl"
qa_data_path = "/root/MyPersonalServerLite/serverlite/stevenai/data/rag_qa.json"

docs_index_path = "/root/MyPersonalServerLite/serverlite/stevenai/models/docs_index.faiss"
docs_meta_path = "/root/MyPersonalServerLite/serverlite/stevenai/models/docs_metadata.pkl"
docs_data_path = "/root/MyPersonalServerLite/serverlite/stevenai/data/rag_document.json"

# === Load embedding model
print("📦 Loading embedding model...")
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# === Load FAISS index and metadata
def load_faiss_index(index_path, meta_path):
    index = faiss.read_index(index_path)
    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

# === Load source documents
def load_documents(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# === Search and display results
def search_and_display(query, model, top_k=3):
    print(f"\n🔍 Query: {query}")

    query_embed = model.encode(
        [query], convert_to_numpy=True
    )

    # Load data
    qa_index, qa_metadatas = load_faiss_index(qa_index_path, qa_meta_path)
    docs_index, docs_metadatas = load_faiss_index(docs_index_path, docs_meta_path)

    qa_data = load_documents(qa_data_path)
    docs_data = load_documents(docs_data_path)

    qa_documents = [entry["content"] for entry in qa_data]
    docs_documents = [entry["content"] for entry in docs_data]

    # Search
    D_qa, I_qa = qa_index.search(query_embed, k=top_k)
    D_docs, I_docs = docs_index.search(query_embed, k=top_k)

    seen_ids = set()

    # Display QA results
    print("\n🎯 Top QA Results:")
    for idx in I_qa[0]:
        meta = qa_metadatas[idx]
        qa_id = meta.get("id")
        print(qa_id)
        if qa_id in seen_ids:
            continue
        seen_ids.add(qa_id)
        q = qa_documents[idx]
        a = meta.get("answer", "[No answer]")
        source = meta.get("section", "N/A")
        print(f"Q: {q}\nA: {a}\nSource: {source}\n---")

    # Display Docs results
    print("\n📄 Top Docs Results:")
    for idx in I_docs[0]:
        meta = docs_metadatas[idx]
        doc_id = meta.get("id")
        print(doc_id)
        if doc_id in seen_ids:
            continue
        seen_ids.add(doc_id)
        doc = docs_documents[idx]
        source = meta.get("section", "N/A")
        print(f"Doc: {doc}\nSource: {source}\n---")


# === Run the query
if __name__ == "__main__":
    query = "Who is your supervisor?"
    search_and_display(query, model, top_k=3)
