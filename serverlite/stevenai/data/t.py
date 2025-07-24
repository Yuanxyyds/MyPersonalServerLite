import json

def convert_to_rag_format(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as infile:
        original_data = json.load(infile)

    rag_formatted = []
    for item in original_data:
        user_msg = next((x["content"] for x in item["input"] if x["role"] == "user"), "")
        assistant_msg = next((x["content"] for x in item["input"] if x["role"] == "assistant"), "")
        section = item.get("section", "unknown")

        rag_formatted.append({
            "content": f"Q: {user_msg}\nA: {assistant_msg}",
            "metadata": {
                "section": section,
                "tags": [],
                "source": "Self Description"
            }
        })

    with open(output_path, "w", encoding="utf-8") as outfile:
        json.dump(rag_formatted, outfile, indent=2, ensure_ascii=False)

    print(f"Converted {len(rag_formatted)} items and saved to '{output_path}'.")

# Example usage:
convert_to_rag_format("about_me.json", "rag_dataset.json")
