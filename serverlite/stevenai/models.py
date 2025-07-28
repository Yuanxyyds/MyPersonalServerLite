from django.db import models
import json
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings


class RAGSearchService:
    def __init__(self):
        print("📦 Initializing RAGSearchService...")

        # === File paths (customize as needed) ===
        self.qa_index_path = settings.QA_INDEX_PATH
        self.qa_meta_path = settings.QA_META_PATH
        self.qa_data_path = settings.QA_DATA_PATH

        self.docs_index_path = settings.DOCS_INDEX_PATH
        self.docs_meta_path = settings.DOCS_META_PATH
        self.docs_data_path = settings.DOCS_DATA_PATH

        # === Load embedding model
        self.model = SentenceTransformer("BAAI/bge-large-en-v1.5")

        # === Load indexes and metadata
        self.qa_index, self.qa_metadatas = self._load_faiss_index(
            self.qa_index_path, self.qa_meta_path
        )
        self.docs_index, self.docs_metadatas = self._load_faiss_index(
            self.docs_index_path, self.docs_meta_path
        )

        # === Load original documents
        self.qa_data = self._load_documents(self.qa_data_path)
        self.docs_data = self._load_documents(self.docs_data_path)

        self.qa_documents = [entry["content"] for entry in self.qa_data]
        self.docs_documents = [entry["content"] for entry in self.docs_data]

    def _load_faiss_index(self, index_path, meta_path):
        index = faiss.read_index(index_path)
        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata

    def _load_documents(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def search(self, query, top_k=3, include_qa=True, include_docs=True):
        print(f"\n🔍 Query: {query}")
        query_embed = self.model.encode([query], convert_to_numpy=True)
        seen_ids = set()
        results = {"qa": [], "docs": []}

        if include_qa:
            D_qa, I_qa = self.qa_index.search(query_embed, k=top_k)
            for idx in I_qa[0]:
                meta = self.qa_metadatas[idx]
                qa_id = meta.get("id")
                if qa_id in seen_ids:
                    continue
                seen_ids.add(qa_id)
                results["qa"].append(
                    {
                        "question": self.qa_documents[idx],
                        "answer": meta.get("answer", "[No answer]"),
                        "source": meta.get("section", "N/A"),
                    }
                )

        if include_docs:
            D_docs, I_docs = self.docs_index.search(query_embed, k=top_k)
            for idx in I_docs[0]:
                meta = self.docs_metadatas[idx]
                doc_id = meta.get("id")
                if doc_id in seen_ids:
                    continue
                seen_ids.add(doc_id)
                results["docs"].append(
                    {
                        "doc": self.docs_documents[idx],
                        "source": meta.get("section", "N/A"),
                    }
                )

        return results
