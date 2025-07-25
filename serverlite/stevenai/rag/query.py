import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import json

# === Load QA index and metadata ===
qa_index = faiss.read_index("qa_index.faiss")
with open("qa_metadata.pkl", "rb") as f:
    qa_metadatas = pickle.load(f)

# === Load Docs index and metadata ===
docs_index = faiss.read_index("docs_index.faiss")
with open("docs_metadata.pkl", "rb") as f:
    docs_metadatas = pickle.load(f)

# === Load source texts (used for display)
with open("/root/MyPersonalServerLite/serverlite/stevenai/data/rag_dataset_questions_only.json", "r") as f:
    qa_data = json.load(f)
with open("/root/MyPersonalServerLite/serverlite/stevenai/data/rag_docs.json", "r") as f:
    docs_data = json.load(f)

qa_documents = [entry["content"] for entry in qa_data]
docs_documents = [entry["content"] for entry in docs_data]

# === Load embedding model
model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# === Encode query
query = "Can you give me some advice in career or enterprenuership?"
query_embed = model.encode(["Represent this sentence for retrieval: " + query], convert_to_numpy=True)

# === Search top-k from each index
top_k = 3
D_qa, I_qa = qa_index.search(query_embed, k=top_k)
D_docs, I_docs = docs_index.search(query_embed, k=top_k)

# === Display Results
print("\n🎯 Top QA Results:")
for idx in I_qa[0]:
    q = qa_documents[idx]
    a = qa_metadatas[idx].get("answer", "[No answer]")
    print(f"Q: {q}\nA: {a}\n---")

print("\n📄 Top Docs Results:")
for idx in I_docs[0]:
    doc = docs_documents[idx]
    meta = docs_metadatas[idx]
    print(f"Doc: {doc}\nSource: {meta.get('section', 'N/A')}\n---")
