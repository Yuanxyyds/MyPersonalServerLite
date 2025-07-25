import json

# Load original dataset
with open("serverlite/stevenai/data/rag_dataset.json", "r") as f:
    data = json.load(f)

# Convert
converted_data = []
for entry in data:
    full_text = entry["content"]
    metadata = entry.get("metadata", {})
    
    if "Q:" in full_text and "A:" in full_text:
        q_part, a_part = full_text.split("A:", 1)
        question = q_part.replace("Q:", "").strip()
        answer = a_part.strip()
        
        new_entry = {
            "content": question,
            "metadata": {
                "answer": answer,
                "section": metadata.get("section", ""),
                "source": metadata.get("source", "")
            }
        }
        converted_data.append(new_entry)
    else:
        print(f"Skipping malformed entry: {full_text[:50]}...")

# Save to new JSON
with open("rag_dataset_questions_only.json", "w") as f:
    json.dump(converted_data, f, indent=2, ensure_ascii=False)

print(f"✅ Converted {len(converted_data)} entries and saved to rag_dataset_questions_only.json")
