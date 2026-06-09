import json
import pickle
from pymongo import MongoClient
import toml
import os

def ingest_additional_data():
    secrets_path = ".streamlit/secrets.toml"
    if not os.path.exists(secrets_path):
        print("Secrets file not found.")
        return

    secrets = toml.load(secrets_path)
    client = MongoClient(secrets.get("MONGO_URI"))
    db = client["poll_abinit"]

    # 1. Ingest gold_answers
    with open("qa_data/gold_qa_sample_100.json", "r") as f:
        data = json.load(f)
    
    gold_docs = [{"question_index": i, "answer": item["answer"]} for i, item in enumerate(data)]
    db["gold_answers"].insert_many(gold_docs)
    print("Inserted gold answers.")

    # 2. Ingest eval_llm_rag
    with open("qa_data/eval_sample_100_reranker_flash_latest_larger_kb.pkl", "rb") as f:
        eval_data = pickle.load(f)
    
    # Structure: {"llm": [{'feedback':str, "score":int},...], "rag": [...]}
    # The order matches questions 0-99.
    
    eval_docs = []
    for i in range(len(eval_data["llm"])):
        eval_docs.append({
            "question_index": i,
            "llm": eval_data["llm"][i],
            "rag": eval_data["rag"][i]
        })
    
    db["eval_llm_rag"].insert_many(eval_docs)
    print("Inserted evaluations.")

    client.close()

if __name__ == "__main__":
    ingest_additional_data()
