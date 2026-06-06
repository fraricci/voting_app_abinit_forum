import os
from pymongo import MongoClient
import toml

def get_mongo_uri():
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        secrets = toml.load(secrets_path)
        return secrets.get("MONGO_URI")
    return None

def reset_votes():
    uri = get_mongo_uri()
    if not uri:
        print("Could not find MONGO_URI in .streamlit/secrets.toml")
        return

    client = MongoClient(uri)
    db = client["poll_abinit"]
    
    votes_col = db["votes"]
    
    # Drop only the votes collection
    votes_col.drop()
    
    client.close()
    print("Successfully reset all votes.")

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete ALL votes? (yes/no): ")
    if confirm.lower() == "yes":
        reset_votes()
    else:
        print("Reset cancelled.")
