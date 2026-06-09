import streamlit as st
from pymongo import MongoClient
import toml
import os
import pandas as pd
from bson import ObjectId

# Database config
DB_NAME = "poll_abinit"

def get_db():
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        secrets = toml.load(secrets_path)
        uri = secrets.get("MONGO_URI")
        client = MongoClient(uri)
        return client[DB_NAME]
    return None

st.title("Question Analysis Dashboard")

db = get_db()
if db is None:
    st.error("Could not connect to database. Check secrets.")
    st.stop()

# Load questions
questions = list(db["questions"].find().sort("_id", 1))

# Create options for dropdown
options = {}
for idx, q in enumerate(questions):
    label = f"Q{idx+1}: {q['text'][:50]}..."
    options[label] = q

# Dropdown
selected_label = st.selectbox("Select a question:", list(options.keys()))
selected_q = options[selected_label]

# Load votes
votes = list(db["votes"].find({"question_id": selected_q["_id"]}))

# To load gold answer and evaluations, we need the question index.
# The questions were sorted by text. We need to find the index of the selected question.
q_idx = questions.index(selected_q)

# Load gold answer
gold_ans = db["gold_answers"].find_one({"question_index": q_idx})

# Load evaluations
eval_data = db["eval_llm_rag"].find_one({"question_index": q_idx})

st.subheader("Votes:")
if not votes:
    st.write("No votes for this question.")
else:
    # Prepare data for table
    vote_data = []
    for v in votes:
        ratings = v.get("votes", {})
        
        # Initialize ratings for this vote
        row = {
            "ID": str(v["_id"]),
            "Time": v["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "RAG": "N/A",
            "LLM": "N/A"
        }
        
        for ans_id, rating in ratings.items():
            ans = db["answers"].find_one({"_id": ObjectId(ans_id)})
            if ans:
                ans_type = ans.get("type", "Unknown")
                row[ans_type] = rating
                
        vote_data.append(row)
        
    # Display as table
    st.table(pd.DataFrame(vote_data))

st.subheader("Full Question:")
st.write(selected_q["text"])

if gold_ans:
    st.subheader("Gold Answer:")
    st.markdown(gold_ans["answer"])

# Load answers
answers = list(db["answers"].find({"question_id": selected_q["_id"]}))
st.subheader("Answers:")

cols = st.columns(2)
# The order of answers in `answers` is usually the order of insertion (RAG, then LLM)
rag_ans = next((a for a in answers if a['type'] == 'RAG'), None)
llm_ans = next((a for a in answers if a['type'] == 'LLM'), None)

with cols[0]:
    if rag_ans:
        st.markdown("**[RAG]**")
        if eval_data and "rag" in eval_data:
            st.write(f"**Score:** {eval_data['rag'].get('score')}")
            with st.expander("Show Feedback"):
                st.write(eval_data['rag'].get('feedback'))
        st.markdown(rag_ans["text"])

with cols[1]:
    if llm_ans:
        st.markdown("**[LLM]**")
        if eval_data and "llm" in eval_data:
            st.write(f"**Score:** {eval_data['llm'].get('score')}")
            with st.expander("Show Feedback"):
                st.write(eval_data['llm'].get('feedback'))
        st.markdown(llm_ans["text"])
