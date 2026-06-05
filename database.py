import streamlit as st
from pymongo import MongoClient
import json
import pickle
import random
from datetime import datetime

# Database config
DB_NAME = "poll_abinit"
COLLECTION_Q = "questions"
COLLECTION_A = "answers"
COLLECTION_V = "votes"

@st.cache_resource
def get_db():
    client = MongoClient(st.secrets["MONGO_URI"])
    return client[DB_NAME]

def ingest_data(question_file, answers_file1, answers_file2):
    db = get_db()
    
    # Check if already ingested
    if db[COLLECTION_Q].count_documents({}) > 0:
        return

    with open(question_file, 'r') as f:
        questions = json.load(f)
        
    with open(answers_file1, 'rb') as f:
        answers1 = pickle.load(f)
    
    with open(answers_file2, 'rb') as f:
        answers2 = pickle.load(f)
        
    def extract_text(content):
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            return "".join([part.get('text', '') for part in content if isinstance(part, dict)])
        return str(content)

    ans1_texts = [extract_text(item[-1][0].content) for item in answers1]
    ans2_texts = [extract_text(item.content) for item in answers2]
    
    for i, q in enumerate(questions):
        q_doc = {"text": q['question']}
        q_id = db[COLLECTION_Q].insert_one(q_doc).inserted_id
        
        a_docs = [
            {"question_id": q_id, "text": ans1_texts[i], "type": "RAG"},
            {"question_id": q_id, "text": ans2_texts[i], "type": "LLM"}
        ]
        db[COLLECTION_A].insert_many(a_docs)

def get_random_question_pair():
    db = get_db()
    
    # Fetch a random question
    q = db[COLLECTION_Q].aggregate([{"$sample": {"size": 1}}]).next()
    
    # Fetch answers for this question
    answers = list(db[COLLECTION_A].find({"question_id": q["_id"]}))
    
    return q["_id"], q["text"], answers

def record_vote(question_id, winner_id, loser_id):
    db = get_db()
    db[COLLECTION_V].insert_one({
        "question_id": question_id,
        "winner_answer_id": winner_id,
        "loser_answer_id": loser_id,
        "timestamp": datetime.now()
    })

def validate_vote(question_id, winner_id, loser_id):
    db = get_db()
    winner_exists = db[COLLECTION_A].count_documents({"_id": winner_id}) > 0
    loser_exists = db[COLLECTION_A].count_documents({"_id": loser_id}) > 0
    return winner_exists and loser_exists
