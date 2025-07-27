import json
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# === File paths ===
qa_path = "/root/MyPersonalServerLite/serverlite/stevenai/data/rag_qa.json"
docs_path = "/root/MyPersonalServerLite/serverlite/stevenai/data/rag_document.json"


# === Load datasets ===
def load_dataset(path):
    with open(path, "r") as f:
        return json.load(f)


# === Format section + tags as prefix
def format_with_prefix(entry):
    meta = entry.get("metadata", {})
    source_type = meta.get("source_type", "")
    if source_type == "QA":
        return entry["content"]

    section = meta.get("section", "")
    tags = meta.get("tags", [])
    tag_str = ", ".join(tags) if tags else ""
    prefix = f"{section}"
    if tag_str:
        prefix += f" - {tag_str}"
    return f"{prefix}: {entry['content']}".strip()


# === Embed and save index function ===
def embed_dataset(data, source_type, model, batch_size, index_path, meta_path):
    print(f"📥 Processing {source_type} entries...")
    documents = []
    metadatas = []

    for entry in tqdm(data):
        documents.append(format_with_prefix(entry))
        metadata = entry["metadata"]
        metadata["source_type"] = source_type
        metadatas.append(metadata)

    print(f"⚙️  Embedding {len(documents)} {source_type} entries...")
    embeddings = model.encode(
        documents, convert_to_numpy=True, batch_size=batch_size, show_progress_bar=True
    )

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, index_path)
    with open(meta_path, "wb") as f:
        pickle.dump(metadatas, f)

    print(
        f"✅ {source_type} done: {len(documents)} entries → {index_path}, {meta_path}\n"
    )


# === Load embedding model
print("📦 Loading embedding model...")
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# === Choose what to embed
qa_data = load_dataset(qa_path)
docs_data = load_dataset(docs_path)

# === Example usage
embed_dataset(
    data=qa_data,
    source_type="QA",
    model=model,
    batch_size=16,
    index_path="/root/MyPersonalServerLite/serverlite/stevenai/models/qa_index.faiss",
    meta_path="/root/MyPersonalServerLite/serverlite/stevenai/models/qa_metadata.pkl",
)

embed_dataset(
    data=docs_data,
    source_type="Docs",
    model=model,
    batch_size=16,
    index_path="/root/MyPersonalServerLite/serverlite/stevenai/models/docs_index.faiss",
    meta_path="/root/MyPersonalServerLite/serverlite/stevenai/models/docs_metadata.pkl",
)
