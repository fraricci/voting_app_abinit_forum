import csv
import os
from pymongo import MongoClient
import streamlit as st

# We need to load the MONGO_URI from the same location the app does.
# Since this is a standalone script, we can load it from the secrets file directly.
# A simple way for a script is to parse the .streamlit/secrets.toml file.
import toml

def get_mongo_uri():
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        secrets = toml.load(secrets_path)
        return secrets.get("MONGO_URI")
    return None

DB_NAME = "poll_abinit"
OUTPUT_CSV = "votes_export.csv"

def export_votes_to_csv():
    uri = get_mongo_uri()
    if not uri:
        print("Could not find MONGO_URI in .streamlit/secrets.toml")
        return

    client = MongoClient(uri)
    db = client[DB_NAME]
    
    votes_col = db["votes"]
    questions_col = db["questions"]
    answers_col = db["answers"]
    
    votes = list(votes_col.find())
    
    rag_wins = 0
    llm_wins = 0
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Vote ID', 'Question', 'Winner Answer', 'Loser Answer', 'Timestamp', 'Winner Type'])
        
        for vote in votes:
            q = questions_col.find_one({"_id": vote["question_id"]})
            a_winner = answers_col.find_one({"_id": vote["winner_answer_id"]})
            a_loser = answers_col.find_one({"_id": vote["loser_answer_id"]})
            
            winner_type = a_winner.get("type", "Unknown") if a_winner else "N/A"
            if winner_type == "RAG":
                rag_wins += 1
            elif winner_type == "LLM":
                llm_wins += 1
            
            writer.writerow([
                str(vote["_id"]),
                q["text"] if q else "N/A",
                a_winner["text"] if a_winner else "N/A",
                a_loser["text"] if a_loser else "N/A",
                vote["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
                winner_type
            ])
        
    client.close()
    print(f"Successfully exported {len(votes)} votes to {OUTPUT_CSV}")
    print(f"Total RAG wins: {rag_wins}")
    print(f"Total LLM wins: {llm_wins}")

if __name__ == "__main__":
    export_votes_to_csv()
