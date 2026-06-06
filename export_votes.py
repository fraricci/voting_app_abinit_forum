import csv
import os
from pymongo import MongoClient
import toml
from bson import ObjectId

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
    
    rag_up = 0
    rag_down = 0
    llm_up = 0
    llm_down = 0
    both_up = 0
    
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Vote ID', 'Question', 'Answer 1 (Type)', 'Vote 1', 'Answer 2 (Type)', 'Vote 2', 'Timestamp'])
        
        for vote in votes:
            q = questions_col.find_one({"_id": vote["question_id"]})
            q_text = q["text"] if q else "N/A"
            
            vote_dict = vote.get("votes", {})
            ans_ids = list(vote_dict.keys())
            
            # Map answers to types
            ratings = []
            for ans_id in ans_ids:
                a = answers_col.find_one({"_id": ObjectId(ans_id)})
                # Map long label back to 'Up' or 'Down'
                raw_vote = vote_dict[ans_id]
                vote_val = "Up" if "Up" in raw_vote else ("Down" if "Down" in raw_vote else "Unknown")
                
                if a:
                    ratings.append({"type": a.get("type"), "vote": vote_val})
            
            # Count metrics
            is_both_up = True
            for r in ratings:
                if r["type"] == "RAG":
                    if r["vote"] == "Up": rag_up += 1
                    else: rag_down += 1
                elif r["type"] == "LLM":
                    if r["vote"] == "Up": llm_up += 1
                    else: llm_down += 1
                
                if r["vote"] != "Up":
                    is_both_up = False
            
            if len(ratings) == 2 and is_both_up:
                both_up += 1
            
            writer.writerow([
                str(vote["_id"]),
                q_text,
                ratings[0]["type"] if len(ratings) > 0 else "N/A",
                ratings[0]["vote"] if len(ratings) > 0 else "N/A",
                ratings[1]["type"] if len(ratings) > 1 else "N/A",
                ratings[1]["vote"] if len(ratings) > 1 else "N/A",
                vote["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            ])
        
    client.close()
    print(f"Successfully exported {len(votes)} votes to {OUTPUT_CSV}")
    print("-" * 30)
    print(f"Stats:")
    print(f"  RAG Up:   {rag_up}")
    print(f"  RAG Down: {rag_down}")
    print(f"  LLM Up:   {llm_up}")
    print(f"  LLM Down: {llm_down}")
    print(f"  Cases with Both Up: {both_up}")

if __name__ == "__main__":
    export_votes_to_csv()
